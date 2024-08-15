import logging
from django.utils import timezone

from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from django.core.mail import send_mail

from ...models import Post


logger = logging.getLogger(__name__)


def send_weekly_updates():
    User = get_user_model()
    users = User.objects.all()
    for user in users:
        if not user.get_subscribe():
            continue

        subscribed_categories = user.get_subscribe()
        new_posts = Post.objects.filter(category__in=subscribed_categories, post_time__gte=timezone.now() - timezone.timedelta(days=7))

        if new_posts:
            subject = 'Weekly Update: New Posts in Your Subscribed Categories'
            message = 'Here are the new posts from the categories you are subscribed to:\n\n'

            for post in new_posts:
                message += f'{post.title} - http://127.0.0.1:9000{post.get_absolute_url()}\n'

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )


def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            send_weekly_updates,
            trigger=CronTrigger(day_of_week="sun", hour="00", minute="00"),
            id="send_weekly_updates",
            max_instances=1,
            replace_existing=True,
            )
        logger.info("Added job 'send_weekly_updates'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
