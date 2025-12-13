from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CityViewSet, ProjectViewSet, ClientViewSet,
    ReviewViewSet, BlogPostViewSet,
    ContactViewSet, AchievementViewSet,
    TowerViewSet, FlatViewSet, ProjectImageViewSet, ProjectAmenityViewSet,
    TowerAmenityViewSet, send_otp, verify_otp
)

router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'project-images', ProjectImageViewSet, basename='projectimage')
router.register(r'project-amenities', ProjectAmenityViewSet, basename='projectamenity')
router.register(r'towers', TowerViewSet, basename='tower')
router.register(r'tower-amenities', TowerAmenityViewSet, basename='toweramenity')
router.register(r'flats', FlatViewSet, basename='flat')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'blog', BlogPostViewSet, basename='blog')
router.register(r'contact', ContactViewSet, basename='contact')
router.register(r'achievements', AchievementViewSet, basename='achievement')

urlpatterns = [
    path('', include(router.urls)),
    # Authentication endpoints
    path('auth/send-otp/', send_otp, name='send_otp'),
    path('auth/verify-otp/', verify_otp, name='verify_otp'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

