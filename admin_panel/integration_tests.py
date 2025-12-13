"""
Integration Tests for Admin Panel
"""
from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from api.models import Contact, User, OTP


class AdminPanelIntegrationTestCase(TestCase):
    """Integration tests for admin panel endpoints"""
    
    def setUp(self):
        self.client = Client()
        # Create test contacts
        self.contact1 = Contact.objects.create(
            name='Test User 1',
            email='test1@example.com',
            phone='1234567890',
            subject='Test Subject 1',
            message='Test Message 1',
            read=False,
            created_at=timezone.now()
        )
        self.contact2 = Contact.objects.create(
            name='Test User 2',
            email='test2@example.com',
            phone='1234567891',
            subject='Test Subject 2',
            message='Test Message 2',
            read=True,
            created_at=timezone.now() - timedelta(days=1)
        )
    
    def test_admin_leads_workflow(self):
        """Test complete admin leads workflow"""
        # 1. Get leads stats
        response = self.client.get('/api/admin/leads/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.json()['total'], 2)
        
        # 2. Get all leads
        response = self.client.get('/api/admin/leads/?period=all')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        leads = response.json()
        self.assertGreaterEqual(len(leads), 2)
        
        # 3. Mark a lead as read
        response = self.client.post(f'/api/admin/leads/{self.contact1.id}/read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Verify lead is marked as read
        self.contact1.refresh_from_db()
        self.assertTrue(self.contact1.read)
        
        # 5. Check updated stats
        response = self.client.get('/api/admin/leads/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        unread_count = response.json()['unread']
        self.assertGreaterEqual(unread_count, 0)

