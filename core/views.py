from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Course, Resource, FreeCourse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
def SignUp(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    # Basic validation check
    if not username or not email or not password:
        return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

    # Check if user already exists
    if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
        return Response({"error": "Username or email already exists"}, status=status.HTTP_400_BAD_REQUEST)

    # Create user
    new_user = User.objects.create_user(username=username, email=email, password=password)
    new_user.save()

    # Generate JWT tokens for the newly created user
    refresh = RefreshToken.for_user(new_user)

    return Response({
        "message": "User created successfully",
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetUser(request):        
    user = request.user
    profile = user.profile

    # 2. Get all courses the user HAS bought
    bought_query = profile.bought_courses.all()
    
    # 3. Get all courses the user HAS NOT bought (exclude the ones they own)
    unbought_query = Course.objects.exclude(id__in=bought_query)

    bought_list = [
        {"id": c.id, "title": c.title, "description": c.description, "video_id": c.video_id} 
        for c in bought_query
    ]
    
    unbought_list = [
        {"id": c.id, "title": c.title, "description": c.description, "price": c.price, "coin_reward": c.coin_reward} 
        for c in unbought_query
    ]

    return Response({
        "username": user.username,
        "email": user.email,
        "coins": profile.coins,
        "has_ever_paid": profile.has_ever_paid,
        "bought_courses": bought_list,
        "unbought_courses": unbought_list
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetFreeCourses(request):
    free_courses = list(FreeCourse.objects.values())
    return JsonResponse(free_courses, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetFreeCourse(request, course_id):
    free_course = get_object_or_404(FreeCourse, pk=course_id)
    return Response({
        "title": free_course.title,
        "description": free_course.description,
        "youtube_id": free_course.youtube_id,
        "coin_reward": free_course.coin_reward
    }, status = status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def PurchaseCourse(request):
    user = request.user
    profile = user.profile
    course_id = request.data.get('course_id')

    # 1. Look up the course object safely
    course = get_object_or_404(Course, pk=course_id)

    # 2. Database-level check to prevent double-purchasing
    if profile.bought_courses.filter(id=course_id).exists():
        return Response(
            {'error': "This course has already been purchased"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # This line runs only after successfull payment
    profile.bought_courses.add(course)

    return Response({
        'success': True,
        'message': f'Successfully purchased {course.title}!'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def PurchaseResource(request):
    user = request.user
    profile = user.profile
    resource_id = request.data.get('resource_id')

    resource = get_object_or_404(Resource, pk=resource_id)

    if profile.bought_resources.filter(id = resource_id).exists():
        return Response(
            {'error': "This resource has already been purchased"},
            status = status.HTTP_400_BAD_REQUEST
        )

    if money_price >= 0:
        # Payment code

        profile.bought_resources.add(resource)
        return Response({
            'success': True,
            'message': f'Successfully purchased {resource.title}!'
        }, status=status.HTTP_200_OK)

    else:
        if profile.coins >= resource.coin_price:
            profile.bought_resources.add(resource)
            return Response({
                'success': True,
                'message': f'Successfully purchased {resource.title}!'
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': "Insufficient coins. Watch more courses to get more coins"},
                status = status.HTTP_400_BAD_REQUEST
            )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh_token = request.data.get("refresh")

    if refresh_token:
        RefreshToken(refresh_token).blacklist()

    return Response({"message": "Logged out successfully."})
