"""
URL configuration for nationnine project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="NationNineRealty API",
        default_version='v1',
        description="""
## NationNineRealty API Documentation

### User Authentication (OTP Based)
- `POST /api/auth/send-otp/` - Send OTP to mobile number
- `POST /api/auth/verify-otp/` - Verify OTP and login/register
- `POST /api/auth/complete-registration/` - Complete user registration

### Admin Authentication
- `POST /api/admin/login/` - Admin login with username/password

### Projects
- `GET /api/projects/` - List all projects
- `POST /api/projects/` - Create project (Admin only)
- `GET /api/projects/{id}/` - Get project details
- `PUT /api/projects/{id}/` - Update project (Admin only)
- `DELETE /api/projects/{id}/` - Delete project (Admin only)

### Admin Dashboard
- `GET /api/admin/leads/stats/` - Get leads statistics
- `GET /api/admin/leads/` - List all leads
- `POST /api/admin/leads/{id}/read/` - Mark lead as read
        """,
        contact=openapi.Contact(email="contact@nationnine.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/admin/', include('admin_panel.urls')),  # Admin panel routes
    
    # Swagger API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

