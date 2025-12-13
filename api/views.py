from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
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


class IsCustomAdminUser(BasePermission):
    """
    Custom permission to check if user is admin based on is_admin field.
    For now, we'll allow all authenticated requests since we're using custom auth.
    In production, you should implement proper token-based authentication.
    """
    def has_permission(self, request, view):
        # For now, allow all requests - authentication will be handled via frontend checks
        # In production, implement proper token authentication here
        return True


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
        if self.request.user and hasattr(self.request.user, 'is_admin') and self.request.user.is_admin:
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
        if self.request.user and hasattr(self.request.user, 'is_admin') and self.request.user.is_admin:
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
        if self.request.user and hasattr(self.request.user, 'is_admin') and self.request.user.is_admin:
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
    """Verify OTP and create/login user"""
    try:
        mobile = request.data.get('mobile')
        otp_code = request.data.get('otp_code')
        purpose = request.data.get('purpose', 'login')
        
        if not mobile or not otp_code:
            return Response({
                'error': 'Mobile and OTP code are required',
                'code': 'MISSING_FIELDS'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find valid OTP
        otp = OTP.objects.filter(
            mobile=mobile,
            otp_code=otp_code,
            purpose=purpose,
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
        
        if purpose == 'signup':
            # Get user data
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            email = request.data.get('email', '')
            
            # Create or get user
            user, created = User.objects.get_or_create(
                mobile=mobile,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email if email else None,
                }
            )
            
            if not created:
                # Update user info if exists
                user.first_name = first_name or user.first_name
                user.last_name = last_name or user.last_name
                if email:
                    user.email = email
                user.save()
            
            user.last_login = timezone.now()
            user.save()
            
            serializer = UserSerializer(user)
            user_data = serializer.data
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            return Response({
                'message': 'User registered successfully',
                'user': user_data,
                'tokens': {
                    'access': access_token,
                    'refresh': refresh_token
                }
            }, status=status.HTTP_201_CREATED)
        
        elif purpose == 'login':
            # Get or create user
            user, created = User.objects.get_or_create(
                mobile=mobile,
                defaults={
                    'first_name': 'User',
                    'last_name': '',
                }
            )
            
            # Check if there are any admin users in the system
            admin_count = User.objects.filter(is_admin=True).count()
            
            # If this is a new user and there are no admins, make them admin
            if created and admin_count == 0:
                user.is_admin = True
                print("=" * 60)
                print("🔑 FIRST USER CREATED - AUTOMATICALLY SET AS ADMIN")
                print(f"📱 Mobile: {mobile}")
                print("=" * 60)
            # If user exists but there are no admins, make them admin (for first-time setup)
            elif not created and admin_count == 0:
                user.is_admin = True
                print("=" * 60)
                print("🔑 NO ADMINS FOUND - SETTING USER AS ADMIN")
                print(f"📱 Mobile: {mobile}")
                print("=" * 60)
            
            # Refresh user from database to ensure we have latest data
            user.refresh_from_db()
            user.last_login = timezone.now()
            user.save()
            
            # Print user status for debugging
            print("=" * 60)
            print("👤 USER LOGIN INFO:")
            print(f"📱 Mobile: {user.mobile}")
            print(f"👤 Name: {user.first_name} {user.last_name}")
            print(f"🔑 Is Admin: {user.is_admin}")
            print(f"✅ Active: {user.is_active}")
            print("=" * 60)
            
            serializer = UserSerializer(user)
            user_data = serializer.data
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # Ensure is_admin is in the response
            print(f"📤 Sending user data: {user_data}")
            
            return Response({
                'message': 'Login successful',
                'user': user_data,
                'tokens': {
                    'access': access_token,
                    'refresh': refresh_token
                }
            }, status=status.HTTP_200_OK)
        
        elif purpose == 'contact':
            # Just verify OTP for contact form
            return Response({
                'message': 'OTP verified successfully'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Invalid purpose',
            'code': 'INVALID_PURPOSE'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print("=" * 60)
        print("❌ ERROR IN VERIFY_OTP:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        print("=" * 60)
        return Response({
            'error': f'Failed to verify OTP: {str(e)}',
            'code': 'VERIFICATION_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

