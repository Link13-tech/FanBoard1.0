
from django.urls import path
from .views import PostListView, PostCreateView, PostUpdateView, PostDeleteView, PostDetailView, ManageResponsesView

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('manage-responses/', ManageResponsesView.as_view(), name='manage_responses'),
]
