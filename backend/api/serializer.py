from rest_framework.serializers import ModelSerializer
from rest_framework import serializers 
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['profile_picture']

class UserRegistrationSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'profile']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        Profile.objects.create(user=user, profile_picture=profile_data.get('profile_picture'))
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        instance.save()

        profile = instance.profile
        profile.profile_picture = profile_data.get('profile_picture', profile.profile_picture)
        profile.save()

        return instance
    
class BlogSerializer(ModelSerializer):
    user = UserRegistrationSerializer(read_only=True)
    userVote = serializers.SerializerMethodField()
    class Meta:
        model = Blog
        fields = "__all__"
    
    def get_userVote(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            vote = Vote.objects.filter(user=user, blog=obj).first()
            if vote:
                return vote.vote_type
        return None
    
class ReplySerializer(ModelSerializer):
    user = UserRegistrationSerializer(read_only=True)
    class Meta:
        model = Replies
        fields = "__all__"