from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import *

urlpatterns = [
    path ('blogs/', getBlogs, name="get-blogs"),
    path ('blogs/<str:pk>', getBlog, name= "get-blog"),
    path ('blogs/create/', createBlog, name="create-blog"),
    path('blogs/<int:blog_id>/upvote/', toggle_upvote, name='toggle_upvote'),
    path('blogs/<int:blog_id>/downvote/', toggle_downvote, name='toggle_downvote'),
    path ('blogs/getreplies/<int:pk>/', getReplies, name = 'get-replies'),
    path ('blogs/postreply/<int:pk>/', postReply, name='post-reply'),
    path ('blogs/getmyreplies/<int:pk>/', getMyReplies, name= 'get-my-replies'),
    path ('blogs/deletereply/<int:pk>/', deleteMyReply, name='delete-my-reply'),
    path ('blogs/getmyblogs/<str:username>/', getMyBlogs, name = "get-my-blogs"),
    path ('blogs/getmyblog/<str:pk>', getMyBlog, name = "get-my-blog"),
    path ('blogs/updatemyblog/<str:pk>/', updateMyBlog, name="update-my-blog"),
    path ('blogs/deletemyblog/<str:pk>/', deleteMyBlog, name="delete-my-blog"),
    path ('<str:username>/', getMyProfile, name="get-my-profile"),
    path ('<str:username>/update/', updateMyProfile, name= "update-my-profile"),
    path ('user/register/', registerUser, name="register"),
    path('user/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),   
]
