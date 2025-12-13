"""
Admin Panel URLs - Separate admin routes
"""
from django.urls import path
from .views import (
    admin_leads_stats,
    admin_leads_list,
    mark_lead_read
)

urlpatterns = [
    path('leads/stats/', admin_leads_stats, name='admin_leads_stats'),
    path('leads/', admin_leads_list, name='admin_leads_list'),
    path('leads/<int:lead_id>/read/', mark_lead_read, name='mark_lead_read'),
]

