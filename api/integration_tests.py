"""
Integration Tests for API
"""
from django.test import TestCase, Client
from django.utils import timezone
from rest_framework import status
from api.models import User, OTP, Contact, Project, City


class AuthenticationIntegrationTestCase(TestCase):
    """Integration tests for authentication flow"""
    
    def setUp(self):
        self.client = Client()
    
    def test_complete_signup_flow(self):
        """Test complete signup flow"""
        # 1. Send OTP
        response = self.client.post('/api/auth/send-otp/', {
            'mobile': '1234567890',
            'purpose': 'signup'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        otp_code = response.json()['otp']
        
        # 2. Verify OTP and create user
        response = self.client.post('/api/auth/verify-otp/', {
            'mobile': '1234567890',
            'otp_code': otp_code,
            'purpose': 'signup',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.json())
        
        # 3. Verify user was created
        user = User.objects.get(mobile='1234567890')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
    
    def test_complete_login_flow(self):
        """Test complete login flow"""
        # 1. Send OTP
        response = self.client.post('/api/auth/send-otp/', {
            'mobile': '1234567890',
            'purpose': 'login'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        otp_code = response.json()['otp']
        
        # 2. Verify OTP and login
        response = self.client.post('/api/auth/verify-otp/', {
            'mobile': '1234567890',
            'otp_code': otp_code,
            'purpose': 'login'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.json())


class ProjectIntegrationTestCase(TestCase):
    """Integration tests for project endpoints"""
    
    def setUp(self):
        self.client = Client()
        self.city = City.objects.create(
            name='Pune',
            state='Maharashtra',
            is_active=True
        )
    
    def test_project_list_and_detail(self):
        """Test listing projects and getting project details"""
        # Create a project
        project = Project.objects.create(
            title='Test Project',
            property_type='residential',
            location='Test Location',
            city=self.city,
            description='Test Description'
        )
        
        # List projects
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        projects = response.json()['results'] if 'results' in response.json() else response.json()
        self.assertGreater(len(projects), 0)
        
        # Get project detail
        response = self.client.get(f'/api/projects/{project.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['title'], 'Test Project')

