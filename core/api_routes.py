from django.urls import path

from .views import *

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
	path('signup/', SignUp, name="sign-up"),
	path('login/', TokenObtainPairView.as_view(), name="login"),
	path('refresh-token/', TokenRefreshView.as_view(), name="refresh-token"),
	path('logout/', logout, name="logout"),

	path('getuser/', GetUser, name="get-user"),
	path('getfreecourses/', GetFreeCourses, name="get-free-courses"),
	path('getfreecourse/<int:course_id>', GetFreeCourse, name="get-free-course"),
	path('purchase-course/', PurchaseCourse, name="purchase-course"),
	path('purchase-resource/', PurchaseResource, name="purchase-resource")
]