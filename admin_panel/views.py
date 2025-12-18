"""
Admin Panel Views - Separate admin logic from user-facing API
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
from api.models import (
    Project, Contact, ProjectImage, ProjectAmenity,
    Tower, Flat, TowerAmenity, City, Client,
    Review, BlogPost, Achievement
)
from api.serializers import (
    ProjectSerializer, ContactSerializer, ProjectImageSerializer,
    ProjectAmenitySerializer, TowerSerializer, FlatSerializer,
    TowerAmenitySerializer, CitySerializer,
    ClientSerializer, ReviewSerializer, BlogPostSerializer,
    AchievementSerializer
)


# Admin Login
@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """Admin login using Django's built-in auth (createsuperuser)"""
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate using Django's built-in auth
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_staff and not user.is_superuser:
            return Response({
                'error': 'Not authorized as admin'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'error': 'Account is deactivated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Admin login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_admin': True,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            },
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Login failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Admin Dashboard Views
@api_view(['GET'])
@permission_classes([AllowAny])  # Frontend checks admin status
def admin_leads_stats(request):
    """Get leads statistics for admin dashboard"""
    try:
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Today's leads
        today_leads = Contact.objects.filter(created_at__date=today).count()
        
        # Yesterday's leads
        yesterday_leads = Contact.objects.filter(created_at__date=yesterday).count()
        
        # Last week's leads
        week_leads = Contact.objects.filter(created_at__date__gte=week_ago).count()
        
        # Last month's leads
        month_leads = Contact.objects.filter(created_at__date__gte=month_ago).count()
        
        # Total leads
        total_leads = Contact.objects.count()
        
        # Unread leads
        unread_leads = Contact.objects.filter(read=False).count()
        
        return Response({
            'today': today_leads,
            'yesterday': yesterday_leads,
            'last_week': week_leads,
            'last_month': month_leads,
            'total': total_leads,
            'unread': unread_leads
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': f'Failed to fetch leads stats: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])  # Frontend checks admin status
def admin_leads_list(request):
    """Get list of leads with filtering"""
    try:
        period = request.query_params.get('period', 'all')
        queryset = Contact.objects.all()
        
        today = timezone.now().date()
        
        if period == 'today':
            queryset = queryset.filter(created_at__date=today)
        elif period == 'yesterday':
            yesterday = today - timedelta(days=1)
            queryset = queryset.filter(created_at__date=yesterday)
        elif period == 'week':
            week_ago = today - timedelta(days=7)
            queryset = queryset.filter(created_at__date__gte=week_ago)
        elif period == 'month':
            month_ago = today - timedelta(days=30)
            queryset = queryset.filter(created_at__date__gte=month_ago)
        # 'all' - no filter
        
        leads = queryset.order_by('-created_at')
        
        serializer = ContactSerializer(leads, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': f'Failed to fetch leads: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # Frontend checks admin status
def mark_lead_read(request, lead_id):
    """Mark a lead as read"""
    try:
        lead = Contact.objects.get(id=lead_id)
        lead.read = True
        lead.save()
        return Response({'message': 'Lead marked as read'}, status=status.HTTP_200_OK)
    except Contact.DoesNotExist:
        return Response({'error': 'Lead not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Failed to mark lead as read: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
