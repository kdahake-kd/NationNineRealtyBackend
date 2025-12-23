from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, BasePermission
from django.http import Http404
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
    ProjectImageSerializer, ProjectAmenitySerializer, TowerAmenitySerializer , ProjectEnquirySerializer
)



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


from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

class ProjectEnquiryCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # 1️⃣ Bind request data to serializer
        serializer = ProjectEnquirySerializer(data=request.data)

        # 2️⃣ Validate data
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3️⃣ Get mobile from validated data
        mobile = serializer.validated_data.get('mobile')

        # 4️⃣ Find user by mobile
        user = User.objects.filter(mobile=mobile).first()
        if not user:
            return Response(
                {'error': 'User not found, please register first'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 5️⃣ Inject user into validated data
        serializer.validated_data['user'] = user

        # 6️⃣ Save enquiry
        enquiry = serializer.save()

        # 7️⃣ Success response
        return Response(
            {
                'message': 'Project enquiry created successfully',
                'data': ProjectEnquirySerializer(enquiry).data
            },
            status=status.HTTP_201_CREATED
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


class ProjectListCreateView(APIView):
    """
    List all projects or create a new project.
    GET: List projects with filtering
    POST: Create new project (Admin only)
    """
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Project.objects.all()
        property_type = self.request.query_params.get('property_type', None)
        transaction_type = self.request.query_params.get('transaction_type', None)
        featured = self.request.query_params.get('featured', None)
        is_hot = self.request.query_params.get('is_hot', None)
        city = self.request.query_params.get('city', None)
        city_id = self.request.query_params.get('city_id', None)
        project_status = self.request.query_params.get('project_status', None)
        flat_type = self.request.query_params.get('flat_type', None)
        search_query = self.request.query_params.get('search', None)
        limit = self.request.query_params.get('limit', None)
        
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        if featured is not None:
            queryset = queryset.filter(featured=featured.lower() == 'true')
        if is_hot is not None:
            queryset = queryset.filter(is_hot=is_hot.lower() == 'true')
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        elif city:
            queryset = queryset.filter(
                Q(city__name__icontains=city) | Q(city_name__icontains=city)
            )
        if project_status:
            queryset = queryset.filter(project_status=project_status)
        if flat_type:
            queryset = queryset.filter(
                Q(available_flat_types__icontains=flat_type) |
                Q(towers__flats__flat_type=flat_type)
            ).distinct()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(city__name__icontains=search_query) |
                Q(city_name__icontains=search_query)
            )
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-created_at')
        
        if limit:
            try:
                queryset = queryset[:int(limit)]
            except ValueError:
                pass
        
        return queryset
    
    def get(self, request):
        queryset = self.get_queryset()
        serializer = ProjectSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        # Check admin permission
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProjectSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(APIView):
    """
    Retrieve, update or delete a project instance.
    GET: Retrieve project (increments views)
    PUT: Update project (Admin only)
    PATCH: Partial update project (Admin only)
    DELETE: Delete project (Admin only)
    """
    permission_classes = [AllowAny]
    
    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        project = self.get_object(pk)
        project.views += 1
        project.save(update_fields=['views'])
        serializer = ProjectSerializer(project, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        project = self.get_object(pk)
        serializer = ProjectSerializer(project, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        project = self.get_object(pk)
        serializer = ProjectSerializer(project, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        project = self.get_object(pk)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClientListCreateView(APIView):
    """List all clients or create a new client"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ClientSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientDetailView(APIView):
    """Retrieve, update or delete a client instance"""
    permission_classes = [AllowAny]
    
    def get_object(self, pk):
        try:
            return Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        client = self.get_object(pk)
        serializer = ClientSerializer(client, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        client = self.get_object(pk)
        serializer = ClientSerializer(client, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        client = self.get_object(pk)
        serializer = ClientSerializer(client, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        client = self.get_object(pk)
        client.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewListCreateView(APIView):
    """List all reviews or create a new review"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        reviews = Review.objects.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailView(APIView):
    """Retrieve, update or delete a review instance"""
    permission_classes = [AllowAny]
    
    def get_object(self, pk):
        try:
            return Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        review = self.get_object(pk)
        serializer = ReviewSerializer(review)
        return Response(serializer.data)
    
    def put(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        review = self.get_object(pk)
        serializer = ReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        review = self.get_object(pk)
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        review = self.get_object(pk)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def review_featured(request):
    """Get featured reviews"""
    featured_reviews = Review.objects.filter(featured=True)
    serializer = ReviewSerializer(featured_reviews, many=True)
    return Response(serializer.data)


class BlogPostListCreateView(APIView):
    """List all blog posts or create a new blog post"""
    permission_classes = [AllowAny]
    
    def get_queryset(self):
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
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(category__icontains=search)
            )
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-created_at')
        
        limit = self.request.query_params.get('limit', None)
        if limit:
            try:
                queryset = queryset[:int(limit)]
            except ValueError:
                pass
        
        return queryset
    
    def get(self, request):
        blog_posts = self.get_queryset()
        serializer = BlogPostSerializer(blog_posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = BlogPostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlogPostDetailView(APIView):
    """Retrieve, update or delete a blog post instance (by slug)"""
    permission_classes = [AllowAny]
    
    def get_object(self, slug):
        try:
            return BlogPost.objects.get(slug=slug)
        except BlogPost.DoesNotExist:
            raise Http404
    
    def get(self, request, slug):
        blog_post = self.get_object(slug)
        blog_post.views += 1
        blog_post.save(update_fields=['views'])
        serializer = BlogPostSerializer(blog_post, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, slug):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        blog_post = self.get_object(slug)
        serializer = BlogPostSerializer(blog_post, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, slug):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        blog_post = self.get_object(slug)
        serializer = BlogPostSerializer(blog_post, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, slug):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        blog_post = self.get_object(slug)
        blog_post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContactListCreateView(APIView):
    """List all contacts or create a new contact"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        contacts = Contact.objects.all()
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        # Anyone can create (contact form)
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactDetailView(APIView):
    """Retrieve, update or delete a contact instance (Admin only)"""
    permission_classes = [IsCustomAdminUser]
    
    def get_object(self, pk):
        try:
            return Contact.objects.get(pk=pk)
        except Contact.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        contact = self.get_object(pk)
        serializer = ContactSerializer(contact)
        return Response(serializer.data)
    
    def put(self, request, pk):
        contact = self.get_object(pk)
        serializer = ContactSerializer(contact, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        contact = self.get_object(pk)
        serializer = ContactSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        contact = self.get_object(pk)
        contact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AchievementListCreateView(APIView):
    """List all achievements or create a new achievement"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        achievements = Achievement.objects.all()
        serializer = AchievementSerializer(achievements, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = AchievementSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AchievementDetailView(APIView):
    """Retrieve, update or delete an achievement instance"""
    permission_classes = [AllowAny]
    
    def get_object(self, pk):
        try:
            return Achievement.objects.get(pk=pk)
        except Achievement.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        achievement = self.get_object(pk)
        serializer = AchievementSerializer(achievement, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        achievement = self.get_object(pk)
        serializer = AchievementSerializer(achievement, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        achievement = self.get_object(pk)
        serializer = AchievementSerializer(achievement, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        achievement = self.get_object(pk)
        achievement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CityListCreateView(APIView):
    """List all cities or create a new city"""
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        is_admin = self.request.user and (
            getattr(self.request.user, 'is_staff', False) or 
            getattr(self.request.user, 'is_superuser', False)
        )
        if is_admin:
            return City.objects.all()
        return City.objects.filter(is_active=True)
    
    def get(self, request):
        cities = self.get_queryset()
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CityDetailView(APIView):
    """Retrieve, update or delete a city instance"""
    permission_classes = [AllowAny]
    
    def get_object(self, pk):
        try:
            return City.objects.get(pk=pk)
        except City.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        city = self.get_object(pk)
        serializer = CitySerializer(city)
        return Response(serializer.data)
    
    def put(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        city = self.get_object(pk)
        serializer = CitySerializer(city, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        city = self.get_object(pk)
        serializer = CitySerializer(city, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        city = self.get_object(pk)
        city.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TowerListCreateView(APIView):
    """List all towers or create a new tower"""
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        is_admin = self.request.user and (
            getattr(self.request.user, 'is_staff', False) or 
            getattr(self.request.user, 'is_superuser', False)
        )
        if is_admin:
            queryset = Tower.objects.all()
        else:
            queryset = Tower.objects.filter(is_active=True)
        
        project_id = self.request.query_params.get('project', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset
    
    def get(self, request):
        towers = self.get_queryset()
        serializer = TowerSerializer(towers, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TowerSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TowerDetailView(APIView):
    """Retrieve, update or delete a tower instance"""
    permission_classes = [AllowAny]
    
    def get_object(self, pk):
        try:
            return Tower.objects.get(pk=pk)
        except Tower.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        tower = self.get_object(pk)
        serializer = TowerSerializer(tower, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        tower = self.get_object(pk)
        serializer = TowerSerializer(tower, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        tower = self.get_object(pk)
        serializer = TowerSerializer(tower, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        tower = self.get_object(pk)
        tower.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectImageListCreateView(APIView):
    """List all project images or create a new project image"""
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = ProjectImage.objects.all()
        project_id = self.request.query_params.get('project', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
    
    def get(self, request):
        images = self.get_queryset()
        serializer = ProjectImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProjectImageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectImageDetailView(APIView):
    """Retrieve, update or delete a project image instance"""
    permission_classes = [AllowAny]
    
    def get_object(self, pk):
        try:
            return ProjectImage.objects.get(pk=pk)
        except ProjectImage.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        image = self.get_object(pk)
        serializer = ProjectImageSerializer(image, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        image = self.get_object(pk)
        serializer = ProjectImageSerializer(image, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        image = self.get_object(pk)
        serializer = ProjectImageSerializer(image, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        image = self.get_object(pk)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectAmenityListCreateView(APIView):
    """List all project amenities or create a new project amenity"""
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = ProjectAmenity.objects.all()
        project_id = self.request.query_params.get('project', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
    
    def get(self, request):
        amenities = self.get_queryset()
        serializer = ProjectAmenitySerializer(amenities, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProjectAmenitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectAmenityDetailView(APIView):
    """Retrieve, update or delete a project amenity instance"""
    permission_classes = [AllowAny]
    
    def get_object(self, pk):
        try:
            return ProjectAmenity.objects.get(pk=pk)
        except ProjectAmenity.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        amenity = self.get_object(pk)
        serializer = ProjectAmenitySerializer(amenity)
        return Response(serializer.data)
    
    def put(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        amenity = self.get_object(pk)
        serializer = ProjectAmenitySerializer(amenity, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        amenity = self.get_object(pk)
        serializer = ProjectAmenitySerializer(amenity, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        amenity = self.get_object(pk)
        amenity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TowerAmenityListCreateView(APIView):
    """List all tower amenities or create a new tower amenity"""
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = TowerAmenity.objects.all()
        tower_id = self.request.query_params.get('tower', None)
        if tower_id:
            queryset = queryset.filter(tower_id=tower_id)
        return queryset
    
    def get(self, request):
        amenities = self.get_queryset()
        serializer = TowerAmenitySerializer(amenities, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TowerAmenitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TowerAmenityDetailView(APIView):
    """Retrieve, update or delete a tower amenity instance"""
    permission_classes = [AllowAny]
    
    def get_object(self, pk):
        try:
            return TowerAmenity.objects.get(pk=pk)
        except TowerAmenity.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        amenity = self.get_object(pk)
        serializer = TowerAmenitySerializer(amenity)
        return Response(serializer.data)
    
    def put(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        amenity = self.get_object(pk)
        serializer = TowerAmenitySerializer(amenity, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        amenity = self.get_object(pk)
        serializer = TowerAmenitySerializer(amenity, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        amenity = self.get_object(pk)
        amenity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FlatListCreateView(APIView):
    """List all flats or create a new flat"""
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Flat.objects.all()
        tower_id = self.request.query_params.get('tower', None)
        flat_type = self.request.query_params.get('flat_type', None)
        status_param = self.request.query_params.get('status', None)
        floor = self.request.query_params.get('floor', None)
        search = self.request.query_params.get('search', None)
        
        if tower_id:
            queryset = queryset.filter(tower_id=tower_id)
        if flat_type:
            queryset = queryset.filter(flat_type=flat_type)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if floor:
            queryset = queryset.filter(floor_number=floor)
        if search:
            queryset = queryset.filter(
                Q(flat_number__icontains=search) |
                Q(flat_type__icontains=search)
            )
        
        # Ordering
        ordering = self.request.query_params.get('ordering', 'floor_number,flat_number')
        if ordering:
            queryset = queryset.order_by(*ordering.split(','))
        else:
            queryset = queryset.order_by('floor_number', 'flat_number')
        
        return queryset
    
    def get(self, request):
        flats = self.get_queryset()
        serializer = FlatSerializer(flats, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = FlatSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FlatDetailView(APIView):
    """Retrieve, update or delete a flat instance"""
    permission_classes = [AllowAny]
    
    def get_object(self, pk):
        try:
            return Flat.objects.get(pk=pk)
        except Flat.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        flat = self.get_object(pk)
        serializer = FlatSerializer(flat, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        flat = self.get_object(pk)
        serializer = FlatSerializer(flat, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        flat = self.get_object(pk)
        serializer = FlatSerializer(flat, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        if not IsCustomAdminUser().has_permission(request, self):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        flat = self.get_object(pk)
        flat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)









