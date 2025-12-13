"""
Unit Tests for Admin Panel
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Contact, User


class AdminLeadsStatsTestCase(TestCase):
    """Test admin leads statistics endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        # Create test contacts
        Contact.objects.create(
            name='Test User 1',
            email='test1@example.com',
            phone='1234567890',
            subject='Test Subject 1',
            message='Test Message 1',
            read=False
        )
        Contact.objects.create(
            name='Test User 2',
            email='test2@example.com',
            phone='1234567891',
            subject='Test Subject 2',
            message='Test Message 2',
            read=True
        )
    
    def test_admin_leads_stats_success(self):
        """Test successful retrieval of leads statistics"""
        response = self.client.get('/api/admin/leads/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('today', response.data)
        self.assertIn('total', response.data)
        self.assertIn('unread', response.data)
    
    def test_admin_leads_stats_unread_count(self):
        """Test unread leads count"""
        response = self.client.get('/api/admin/leads/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['unread'], 0)


class AdminLeadsListTestCase(TestCase):
    """Test admin leads list endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Create contacts for different periods
        Contact.objects.create(
            name='Today User',
            email='today@example.com',
            phone='1234567890',
            subject='Today Subject',
            message='Today Message',
            created_at=timezone.now()
        )
        Contact.objects.create(
            name='Yesterday User',
            email='yesterday@example.com',
            phone='1234567891',
            subject='Yesterday Subject',
            message='Yesterday Message',
            created_at=timezone.now() - timedelta(days=1)
        )
    
    def test_admin_leads_list_all(self):
        """Test retrieving all leads"""
        response = self.client.get('/api/admin/leads/?period=all')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_admin_leads_list_today(self):
        """Test retrieving today's leads"""
        response = self.client.get('/api/admin/leads/?period=today')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_admin_leads_list_yesterday(self):
        """Test retrieving yesterday's leads"""
        response = self.client.get('/api/admin/leads/?period=yesterday')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)


class MarkLeadReadTestCase(TestCase):
    """Test mark lead as read endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.contact = Contact.objects.create(
            name='Test User',
            email='test@example.com',
            phone='1234567890',
            subject='Test Subject',
            message='Test Message',
            read=False
        )
    
    def test_mark_lead_read_success(self):
        """Test successfully marking a lead as read"""
        response = self.client.post(f'/api/admin/leads/{self.contact.id}/read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.contact.refresh_from_db()
        self.assertTrue(self.contact.read)
    
    def test_mark_lead_read_not_found(self):
        """Test marking non-existent lead as read"""
        response = self.client.post('/api/admin/leads/99999/read/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
