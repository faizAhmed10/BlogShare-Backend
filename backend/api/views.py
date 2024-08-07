from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializer import * 
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet

class BlogPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class BlogViewSet(ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    pagination_class = BlogPagination
    
@api_view(['GET'])
def getBlogs(request):
    paginator = BlogPagination()
    blogs = Blog.objects.all()
    result_page = paginator.paginate_queryset(blogs, request)
    serializer = BlogSerializer(result_page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def getBlog(request, pk):
    blog = Blog.objects.get(id=pk)
    serializer = BlogSerializer(blog, context={'request': request}) 
    return Response(serializer.data)

# REACTION RELATED VIEWS
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_upvote(request, blog_id):
    user = request.user
    blog = Blog.objects.get(id=blog_id)
    
    vote, created = Vote.objects.get_or_create(user=user, blog=blog)
    
    if vote.vote_type == 'upvote':
        vote.delete()
        blog.upvotes -= 1
    else:
        vote.vote_type = 'upvote'
        vote.save()
        blog.upvotes += 1
        if not created:
            blog.downvotes -= 1 

    blog.save()
    return Response({'upvotes': blog.upvotes, 'downvotes': blog.downvotes})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_downvote(request, blog_id):
    user = request.user
    blog = Blog.objects.get(id=blog_id)
    
    vote, created = Vote.objects.get_or_create(user=user, blog=blog)
    
    if vote.vote_type == 'downvote':
        vote.delete()
        blog.downvotes -= 1
    else:
        vote.vote_type = 'downvote'
        vote.save()
        blog.downvotes += 1
        if not created:
            blog.upvotes -= 1

    blog.save()
    return Response({'upvotes': blog.upvotes, 'downvotes': blog.downvotes})

# BLOG RELATED VIEWS
@api_view(['POST'])
def createBlog(request):
    try:
        data = request.data
        user = request.user

        # Accessing the image file from the request
        image = request.FILES.get('image')

        # Creating the blog entry with the uploaded image
        blog = Blog.objects.create(
            user=user,
            image=image,
            title=data.get('title'),
            sub_title=data.get('sub_title'),
            body=data.get('blog')
        )

        blog.save()
        return Response("Blog Created!")
    except Exception as e:
        return Response(str(e))

@api_view(['GET'])
def getMyBlogs(request, username):
    try:
        user = User.objects.get(username = username)
        blogs = Blog.objects.filter(user=user)
        serializer = BlogSerializer(blogs, many = True, context={'request': request})
        return Response(serializer.data)
    except Exception as e:
        return Response(str(e))

@api_view(['GET'])
def getMyBlog(request, pk):
    try:
        blog = Blog.objects.get(id=pk)
        serializer = BlogSerializer(blog, many=False, context={'request': request})
        return Response(serializer.data)
    except Exception as e:
        return Response(str(e))
    
@api_view(['PUT'])
def updateMyBlog(request, pk):
    try:
        data = request.data
        image = request.FILES.get('image')
        title = data.get('title')
        sub_title = data.get('sub_title')
        body = data.get('body')
        
        blog = Blog.objects.get(id = pk)
        blog.title = title
        blog.sub_title = sub_title
        blog.body = body
        
        if image:
            blog.image = image
            
        blog.save()
        return Response("Blog updated successfully!")
    except Exception as e:
        return Response(str(e))

@api_view(['DELETE'])
def deleteMyBlog(request, pk):
    try:
        user = request.user
        blog = Blog.objects.get(id = pk)
        blog.delete()
        return Response("Blog deleted successfully!")
    except Exception as e:
        return Response(str(e))

# USER PROFILE RELATED VIEWS
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyProfile(request, username):
    try:
        user = User.objects.get(username=username)
        serializer = UserRegistrationSerializer(user, many=False)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateMyProfile(request, username):
    try:
        user = User.objects.get(username=username)
        data = request.data

        if User.objects.filter(username=data['username']).exclude(pk=user.pk).exists():
            return Response({"detail": "Username already exists!"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        user.username = data['username']
        user.email = data['email']
        user.save()

        profile = user.profile

        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()

        return Response("Profile Updated Successfully!")
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteMyProfile(request, username):
    try:
        user = request.user
        profile = User.objects.get(username = username)
        blogs = Blog.objects.filter(user = user)
        profile.delete()
        blogs.delete()
        return Response("User deleted successfully")
    except Exception as e:
        return Response(str(e))  

# REPLIES RELATED VIEWS
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def postReply(request, pk):
    user = request.user
    data = request.data
    
    if not user.is_authenticated:
        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        blog = Blog.objects.get(id=pk)
    except Blog.DoesNotExist:
        return Response({"detail": "Blog not found."}, status=status.HTTP_404_NOT_FOUND)

    reply_text = data.get('reply')
    if not reply_text:
        return Response({"detail": "Reply text is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        reply = Replies.objects.create(user=user, blog=blog, reply=reply_text)
        reply.save()
        return Response({"detail": "Reply successful!"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyReplies(request, pk):
    user = request.user
    try:
        myreplies = Replies.objects.filter(blog_id = pk, user = user)
        serializer = ReplySerializer(myreplies, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteMyReply(request, pk):
    user = request.user
    try:
        user = User.objects.get(username = user.username)
        reply = Replies.objects.get(id = pk, user = user)
        reply.delete()
        return Response("Reply deleted!")
    except Exception as e:
        return Response({"detail": str(e)}) 

@api_view(['GET'])
def getReplies(request, pk):
    data = request.data
    try:
        replies = Replies.objects.filter(blog_id = pk)
        serializer = ReplySerializer(replies, many = True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST) 

# USER AUTH VIEWS
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    
@api_view(['POST'])
def registerUser(request):
    data = request.data
    try:
        if User.objects.filter(username=data['username']).exists():
            raise Exception("User already exists")
        user = User.objects.create(
            username=data['username'], 
            email=data['email'],
            password=make_password(data['password']),
        )
        user.save()
        serializer = UserRegistrationSerializer(user, many=False)
        return Response(serializer.data)
    except Exception as e:
        message = {'details': str(e)}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)