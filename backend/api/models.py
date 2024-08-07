from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default.png')

    def __str__(self):
        return f'{self.user.username} Profile'
    

class Blog(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, null=True)
    image = models.ImageField(upload_to="blogImg", null=True, blank=True)
    title = models.CharField(max_length=50, null=True, blank=True)
    sub_title = models.CharField(max_length=75, null=True, blank=True)
    body = models.TextField(null=True, blank =True)
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title
    
class Replies(models.Model):
    # replyreply = models.ForeignKey(Replies, on_delete = models.SET_NULL, null = True)
    user = models.ForeignKey(User, on_delete = models.SET_NULL, null=True)
    reply = models.TextField(null=True, blank=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='replies')
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username}: {self.reply[:20]}"


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=10, choices=[('upvote', 'Upvote'), ('downvote', 'Downvote')])
    

    
