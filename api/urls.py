from django.urls import path
from .views import (
    # Projects
    ProjectListCreateView, ProjectDetailView,
    # Clients
    ClientListCreateView, ClientDetailView,
    # Reviews
    ReviewListCreateView, ReviewDetailView, review_featured,
    # Blog Posts
    BlogPostListCreateView, BlogPostDetailView,
    # Contact
    ContactListCreateView, ContactDetailView,
    # Achievements
    AchievementListCreateView, AchievementDetailView,
    # Cities
    CityListCreateView, CityDetailView,
    # Towers
    TowerListCreateView, TowerDetailView,
    # Project Images
    ProjectImageListCreateView, ProjectImageDetailView,
    # Project Amenities
    ProjectAmenityListCreateView, ProjectAmenityDetailView,
    # Tower Amenities
    TowerAmenityListCreateView, TowerAmenityDetailView,
    # Flats
    FlatListCreateView, FlatDetailView,
    # Authentication
    send_otp, verify_otp, complete_registration
)

urlpatterns = [
    # Projects
    path('projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    
    # Clients
    path('clients/', ClientListCreateView.as_view(), name='client-list-create'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
    
    # Reviews
    path('reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
    path('reviews/featured/', review_featured, name='review-featured'),
    
    # Blog Posts
    path('blog/', BlogPostListCreateView.as_view(), name='blog-list-create'),
    path('blog/<str:slug>/', BlogPostDetailView.as_view(), name='blog-detail'),
    
    # Contact
    path('contact/', ContactListCreateView.as_view(), name='contact-list-create'),
    path('contact/<int:pk>/', ContactDetailView.as_view(), name='contact-detail'),
    
    # Achievements
    path('achievements/', AchievementListCreateView.as_view(), name='achievement-list-create'),
    path('achievements/<int:pk>/', AchievementDetailView.as_view(), name='achievement-detail'),
    
    # Cities
    path('cities/', CityListCreateView.as_view(), name='city-list-create'),
    path('cities/<int:pk>/', CityDetailView.as_view(), name='city-detail'),
    
    # Towers
    path('towers/', TowerListCreateView.as_view(), name='tower-list-create'),
    path('towers/<int:pk>/', TowerDetailView.as_view(), name='tower-detail'),
    
    # Project Images
    path('project-images/', ProjectImageListCreateView.as_view(), name='projectimage-list-create'),
    path('project-images/<int:pk>/', ProjectImageDetailView.as_view(), name='projectimage-detail'),
    
    # Project Amenities
    path('project-amenities/', ProjectAmenityListCreateView.as_view(), name='projectamenity-list-create'),
    path('project-amenities/<int:pk>/', ProjectAmenityDetailView.as_view(), name='projectamenity-detail'),
    
    # Tower Amenities
    path('tower-amenities/', TowerAmenityListCreateView.as_view(), name='toweramenity-list-create'),
    path('tower-amenities/<int:pk>/', TowerAmenityDetailView.as_view(), name='toweramenity-detail'),
    
    # Flats
    path('flats/', FlatListCreateView.as_view(), name='flat-list-create'),
    path('flats/<int:pk>/', FlatDetailView.as_view(), name='flat-detail'),
    
    # User Authentication (OTP based)
    path('auth/send-otp/', send_otp, name='send_otp'),
    path('auth/verify-otp/', verify_otp, name='verify_otp'),
    path('auth/complete-registration/', complete_registration, name='complete_registration'),
]
