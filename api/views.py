from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, BasePermission
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
import random
import traceback
from .models import (
    City, Project, Client, Review, BlogPost,
    Contact, Achievement,
    Tower, Flat, User, OTP, ProjectImage, ProjectAmenity, TowerAmenity
)
from .serializers import (
    CitySerializer, ProjectSerializer, ClientSerializer,
    ReviewSerializer, BlogPostSerializer,
    ContactSerializer, AchievementSerializer,
    TowerSerializer, FlatSerializer, UserSerializer, OTPSerializer,
    ProjectImageSerializer, ProjectAmenitySerializer, TowerAmenitySerializer
)


class IsCustomAuthenticated(BasePermission):
    """
    Custom permission to check if user is authenticated via JWT token.
    Validates JWT token and attaches user to request.
    """
    def has_permission(self, request, view):
        jwt_auth = JWTAuthentication()
        try:
            auth_result = jwt_auth.authenticate(request)
            if auth_result:
                user, token = auth_result
                # Attach user to request
                request.user = user
                return True
            return False
        except (InvalidToken, TokenError):
            return False
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return False


class IsCustomAdminUser(IsCustomAuthenticated):
    """
    Custom permission to check if user is Django staff/superuser.
    Admin login uses Django's built-in User model (createsuperuser).
    """
    def has_permission(self, request, view):
        # First check if user is authenticated
        if not super().has_permission(request, view):
            return False
        
        # Check if user is Django staff or superuser
        if hasattr(request.user, 'is_staff') and request.user.is_staff:
            return True
        if hasattr(request.user, 'is_superuser') and request.user.is_superuser:
            return True
        return False


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'location', 'description']
    ordering_fields = ['created_at', 'views', 'price']
    ordering = ['-created_at']
    
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        Allow read-only for everyone, but require admin for create/update/delete.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsCustomAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = Project.objects.all()
        property_type = self.request.query_params.get('property_type', None)
        transaction_type = self.request.query_params.get('transaction_type', None)
        featured = self.request.query_params.get('featured', None)
        is_hot = self.request.query_params.get('is_hot', None)
        
        # New search filters
        city = self.request.query_params.get('city', None)
        city_id = self.request.query_params.get('city_id', None)
        project_status = self.request.query_params.get('project_status', None)
        flat_type = self.request.query_params.get('flat_type', None)
        search_query = self.request.query_params.get('search', None)
        
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        if featured is not None:
            queryset = queryset.filter(featured=featured.lower() == 'true')
        if is_hot is not None:
            queryset = queryset.filter(is_hot=is_hot.lower() == 'true')
        
        # City filter
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        elif city:
            queryset = queryset.filter(
                Q(city__name__icontains=city) | Q(city_name__icontains=city)
            )
        
        # Project status filter
        if project_status:
            queryset = queryset.filter(project_status=project_status)
        
        # Flat type filter - check if project has this flat type
        if flat_type:
            queryset = queryset.filter(
                Q(available_flat_types__icontains=flat_type) |
                Q(towers__flats__flat_type=flat_type)
            ).distinct()
        
        # Search query for project name or locality
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(city__name__icontains=search_query) |
                Q(city_name__icontains=search_query)
            )
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views += 1
        instance.save(update_fields=['views'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsCustomAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsCustomAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_reviews = Review.objects.filter(featured=True)
        serializer = self.get_serializer(featured_reviews, many=True)
        return Response(serializer.data)


class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'category']
    ordering_fields = ['created_at', 'views']
    ordering = ['-created_at']
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsCustomAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        # Admin can see all, public only sees published
        is_admin = self.request.user and (
            getattr(self.request.user, 'is_staff', False) or 
            getattr(self.request.user, 'is_superuser', False)
        )
        if is_admin:
            queryset = BlogPost.objects.all()
        else:
            queryset = BlogPost.objects.filter(published=True)
        project_id = self.request.query_params.get('project', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views += 1
        instance.save(update_fields=['views'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    
    def get_permissions(self):
        # Allow anyone to create (contact form), but only admin to read/update/delete
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsCustomAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        # Admin sees all, public can only create
        return Contact.objects.all()
    
    def perform_create(self, serializer):
        serializer.save()


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsCustomAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsCustomAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        # Admin sees all, public only sees active
        is_admin = self.request.user and (
            getattr(self.request.user, 'is_staff', False) or 
            getattr(self.request.user, 'is_superuser', False)
        )
        if is_admin:
            return City.objects.all()
        return City.objects.filter(is_active=True)


class TowerViewSet(viewsets.ModelViewSet):
    queryset = Tower.objects.all()
    serializer_class = TowerSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsCustomAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        # Admin sees all, public only sees active
        is_admin = self.request.user and (
            getattr(self.request.user, 'is_staff', False) or 
            getattr(self.request.user, 'is_superuser', False)
        )
        if is_admin:
            return Tower.objects.all()
        return Tower.objects.filter(is_active=True)
    
    def get_queryset(self):
        queryset = Tower.objects.filter(is_active=True)
        project_id = self.request.query_params.get('project', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ProjectImageViewSet(viewsets.ModelViewSet):
    queryset = ProjectImage.objects.all()
    serializer_class = ProjectImageSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsCustomAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = ProjectImage.objects.all()
        project_id = self.request.query_params.get('project', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ProjectAmenityViewSet(viewsets.ModelViewSet):
    queryset = ProjectAmenity.objects.all()
    serializer_class = ProjectAmenitySerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsCustomAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = ProjectAmenity.objects.all()
        project_id = self.request.query_params.get('project', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset


class TowerAmenityViewSet(viewsets.ModelViewSet):
    queryset = TowerAmenity.objects.all()
    serializer_class = TowerAmenitySerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsCustomAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = TowerAmenity.objects.all()
        tower_id = self.request.query_params.get('tower', None)
        if tower_id:
            queryset = queryset.filter(tower_id=tower_id)
        return queryset


class FlatViewSet(viewsets.ModelViewSet):
    queryset = Flat.objects.all()
    serializer_class = FlatSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['flat_number', 'flat_type']
    ordering_fields = ['floor_number', 'price', 'carpet_area']
    ordering = ['floor_number', 'flat_number']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsCustomAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = Flat.objects.all()
        tower_id = self.request.query_params.get('tower', None)
        flat_type = self.request.query_params.get('flat_type', None)
        status = self.request.query_params.get('status', None)
        floor = self.request.query_params.get('floor', None)
        
        if tower_id:
            queryset = queryset.filter(tower_id=tower_id)
        if flat_type:
            queryset = queryset.filter(flat_type=flat_type)
        if status:
            queryset = queryset.filter(status=status)
        if floor:
            queryset = queryset.filter(floor_number=floor)
        
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    """Send OTP to mobile number"""
    try:
        print("=" * 60)
        print("📥 OTP REQUEST RECEIVED")
        print("=" * 60)
        print(f"Request Data: {request.data}")
        print(f"Request Method: {request.method}")
        
        mobile = request.data.get('mobile')
        purpose = request.data.get('purpose', 'login')  # signup, login, contact
        
        print(f"Mobile: {mobile}")
        print(f"Purpose: {purpose}")
        
        if not mobile:
            print("=" * 60)
            print("❌ ERROR: Mobile number is required")
            print("=" * 60)
            return Response({'error': 'Mobile number is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Clean mobile number (remove spaces, dashes, etc.)
        mobile = ''.join(filter(str.isdigit, str(mobile)))
        
        if len(mobile) < 10:
            print("=" * 60)
            print(f"❌ ERROR: Invalid mobile number length: {len(mobile)}")
            print("=" * 60)
            return Response({'error': 'Invalid mobile number'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        
        # Set expiry to 10 minutes from now
        expires_at = timezone.now() + timedelta(minutes=10)
        
        # Invalidate old OTPs for this mobile
        OTP.objects.filter(mobile=mobile, is_verified=False, expires_at__gt=timezone.now()).update(is_verified=True)
        
        # Create new OTP
        try:
            otp = OTP.objects.create(
                mobile=mobile,
                otp_code=otp_code,
                purpose=purpose,
                expires_at=expires_at
            )
            print(f"✅ OTP created in database: ID {otp.id}")
        except Exception as db_error:
            print("=" * 60)
            print(f"❌ DATABASE ERROR: {str(db_error)}")
            print(f"Traceback: {traceback.format_exc()}")
            print("=" * 60)
            return Response({
                'error': f'Database error: {str(db_error)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Print OTP in terminal for testing
        print("=" * 60)
        print("🔐 OTP GENERATED FOR TESTING")
        print("=" * 60)
        print(f"📱 Mobile Number: {mobile}")
        print(f"🎯 Purpose: {purpose.upper()}")
        print(f"🔑 OTP Code: {otp_code}")
        print(f"⏰ Expires At: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print(f"✅ Enter this OTP in the frontend: {otp_code}")
        print("=" * 60)
        print()
        
        return Response({
            'message': 'OTP sent successfully',
            'otp': otp_code  # Remove this in production
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print("=" * 60)
        print("❌ ERROR IN SEND_OTP:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        print("=" * 60)
        return Response({
            'error': f'Failed to send OTP: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Verify OTP for normal users.
    Flow:
    - If user exists and is_registered=True -> Login directly
    - If user exists but is_registered=False -> Need to complete profile
    - If user doesn't exist -> Create user, need to complete profile
    """
    try:
        mobile = request.data.get('mobile')
        otp_code = request.data.get('otp_code')
        
        if not mobile or not otp_code:
            return Response({
                'error': 'Mobile and OTP code are required',
                'code': 'MISSING_FIELDS'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find valid OTP (check both login and signup purposes)
        otp = OTP.objects.filter(
            mobile=mobile,
            otp_code=otp_code,
            is_verified=False,
            expires_at__gt=timezone.now()
        ).first()
        
        if not otp:
            return Response({
                'error': 'Invalid or expired OTP',
                'code': 'INVALID_OTP'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark OTP as verified
        otp.is_verified = True
        otp.save()
        
        # Check if user exists
        user = User.objects.filter(mobile=mobile).first()
        
        if user and user.is_registered:
            # User exists and is registered - Login directly
            user.last_login = timezone.now()
            user.save()
            
            serializer = UserSerializer(user)
            access_token = AccessToken.for_user(user)
            
            return Response({
                'message': 'Login successful',
                'user': serializer.data,
                'access_token': str(access_token),
                'needs_registration': False
            }, status=status.HTTP_200_OK)
        
        elif user and not user.is_registered:
            # User exists but not registered - Need profile completion
            return Response({
                'message': 'OTP verified. Please complete your profile.',
                'needs_registration': True,
                'mobile': mobile
            }, status=status.HTTP_200_OK)
        
        else:
            # New user - Create and need profile completion
            user = User.objects.create(mobile=mobile, is_registered=False)
            return Response({
                'message': 'OTP verified. Please complete your profile.',
                'needs_registration': True,
                'mobile': mobile
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        print(f"❌ ERROR IN VERIFY_OTP: {str(e)}")
        return Response({
            'error': f'Failed to verify OTP: {str(e)}',
            'code': 'VERIFICATION_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def complete_registration(request):
    """Complete user registration after OTP verification"""
    try:
        mobile = request.data.get('mobile')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email', '')
        
        if not mobile or not first_name or not last_name:
            return Response({
                'error': 'Mobile, first name and last name are required',
                'code': 'MISSING_FIELDS'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(mobile=mobile).first()
        
        if not user:
            return Response({
                'error': 'User not found. Please verify OTP first.',
                'code': 'USER_NOT_FOUND'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Update user profile
        user.first_name = first_name
        user.last_name = last_name
        if email:
            user.email = email
        user.is_registered = True
        user.last_login = timezone.now()
        user.save()
        
        serializer = UserSerializer(user)
        access_token = AccessToken.for_user(user)
        
        return Response({
            'message': 'Registration successful',
            'user': serializer.data,
            'access_token': str(access_token)
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"❌ ERROR IN COMPLETE_REGISTRATION: {str(e)}")
        return Response({
            'error': f'Registration failed: {str(e)}',
            'code': 'REGISTRATION_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

