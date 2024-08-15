
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from .models import Post, Response
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin


class PostListView(ListView):
    model = Post
    template_name = 'board/post_list.html'
    context_object_name = 'posts'
    ordering = '-post_time'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        selected_category = self.request.GET.get('category')
        if selected_category:
            queryset = queryset.filter(category=selected_category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Post.CATEGORY_CHOICES
        context['selected_category'] = self.request.GET.get('category', '')
        for post in context['posts']:
            post.first_image = post.get_first_image()
            post.first_video = post.get_first_video()
            post.content_excerpt = post.get_content_excerpt()
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'board/post_detail.html'
    context_object_name = 'post'

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        if request.user.is_authenticated:
            if request.user == post.author:
                messages.error(request, 'Вы не можете оставить отзыв на свой собственный пост.')
                return redirect('post_detail', pk=post.pk)

            response_text = request.POST.get('response')

            Response.objects.create(
                post=post,
                author=request.user,
                content=response_text
            )

            send_mail(
                'Новый отзыв на твой пост',
                f'Ты получил новый отзыв: {response_text}',
                settings.DEFAULT_FROM_EMAIL,
                [post.author.email],
                fail_silently=False,
            )
            messages.success(request, 'Ваш отзыв был отправлен.')
            return redirect('post_detail', pk=post.pk)
        else:
            return redirect(f'/accounts/login/?next={request.path}')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'board/post_form.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'board/post_form.html'
    success_url = reverse_lazy('post_list')

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'board/post_delete.html'
    success_url = reverse_lazy('post_list')

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)


class ManageResponsesView(LoginRequiredMixin, ListView):
    model = Response
    template_name = 'board/manage_responses.html'
    context_object_name = 'responses'

    def get_queryset(self):
        queryset = Response.objects.filter(post__author=self.request.user)

        selected_post = self.request.GET.get('post')
        if selected_post:
            queryset = queryset.filter(post__id=selected_post)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(author=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        response_id = request.POST.get('response_id')
        response = get_object_or_404(Response, id=response_id)

        if action == 'accept':
            response.accepted = True
            response.save()
            self.send_email(response.author, response.post, 'accepted')
        elif action == 'delete':
            self.send_email(response.author, response.post, 'deleted')
            response.delete()
        else:
            messages.error(request, 'Неизвестное действие!')

        return redirect('manage_responses')

    @staticmethod
    def send_email(user, post, action_type):
        if action_type == 'accepted':
            subject = 'Ваш отклик принят'
            message = f'Ваш отклик на объявление "{post.title}" был принят.'
        elif action_type == 'deleted':
            subject = 'Ваш отклик удалён'
            message = f'Ваш отклик на объявление "{post.title}" был удалён.'
        else:
            subject = 'Неизвестное действие'
            message = 'Произошло неизвестное действие с вашим откликом.'

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


@login_required
def subscribe_category(request, category_name):
    if category_name in request.user.get_subscribe():
        request.user.remove_subscription(category_name)
    else:
        request.user.add_subscription(category_name)
    return redirect(request.META.get('HTTP_REFERER', 'post_list'))
