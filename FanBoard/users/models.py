import json

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    code = models.CharField(max_length=15, blank=True, null=True)
    subscribe = models.TextField(blank=True, default='[]')  # Список категорий в формате JSON

    def get_subscribe(self):
        return json.loads(self.subscribe)

    def add_subscription(self, category):
        subscriptions = self.get_subscribe()
        if category not in subscriptions:
            subscriptions.append(category)
            self.subscribe = json.dumps(subscriptions)
            self.save()

    def remove_subscription(self, category):
        subscriptions = self.get_subscribe()
        if category in subscriptions:
            subscriptions.remove(category)
            self.subscribe = json.dumps(subscriptions)
            self.save()
