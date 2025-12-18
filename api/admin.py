from django.contrib import admin
from .models import (
    City, Project, Client, Review, BlogPost, 
    Contact, Achievement,
    ProjectImage, ProjectAmenity, Tower, TowerAmenity, Flat, User, OTP
)


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('image', 'title', 'category', 'order')


class ProjectAmenityInline(admin.TabularInline):
    model = ProjectAmenity
    extra = 1
    fields = ('name', 'icon', 'order')


class TowerInline(admin.TabularInline):
    model = Tower
    extra = 0
    fields = ('name', 'tower_number', 'total_floors', 'booking_status', 'is_active', 'order')


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'state', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'state', 'created_at']
    search_fields = ['name', 'state']
    list_editable = ['is_active', 'order']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'id_number', 'property_type', 'transaction_type', 'project_status', 'city_name', 'location', 'featured', 'is_hot', 'views', 'created_at']
    list_filter = ['property_type', 'transaction_type', 'project_status', 'featured', 'is_hot', 'city', 'created_at']
    search_fields = ['title', 'location', 'description', 'city__name', 'city_name', 'state', 'id_number', 'rera_number']
    list_editable = ['featured', 'is_hot']
    readonly_fields = ['views', 'created_at', 'updated_at']
    inlines = [ProjectImageInline, ProjectAmenityInline, TowerInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'id_number', 'property_type', 'transaction_type', 'project_status', 'description', 'about_listing')
        }),
        ('Location', {
            'fields': ('location', 'city', 'city_name', 'state', 'map_location')
        }),
        ('Search Filters', {
            'fields': ('available_flat_types',),
            'description': 'These fields are used for search filtering'
        }),
        ('Project Details', {
            'fields': ('rera_number', 'land_area', 'amenities_area', 'total_units', 'total_towers', 'developer_name')
        }),
        ('Media & Pricing', {
            'fields': ('cover_image', 'price')
        }),
        ('Specifications', {
            'fields': ('structure', 'flooring', 'kitchen', 'electrical', 'doors', 'plaster', 'windows', 'toilet', 'security_safety', 'paint', 'plumbing', 'lift'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('featured', 'is_hot', 'views')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'created_at']
    list_editable = ['order']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'designation', 'rating', 'featured', 'created_at']
    list_filter = ['rating', 'featured', 'created_at']
    search_fields = ['customer_name', 'review_text']
    list_editable = ['featured']
    readonly_fields = ['created_at']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'author', 'category', 'published', 'views', 'created_at']
    list_filter = ['published', 'category', 'created_at', 'project']
    search_fields = ['title', 'content', 'project__title']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['published']
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'title', 'slug', 'author', 'category', 'published')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image', 'video')
        }),
        ('Statistics', {
            'fields': ('views',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['views', 'created_at', 'updated_at']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'project', 'subject', 'read', 'created_at']
    list_filter = ['read', 'created_at', 'project']
    list_editable = ['read']
    search_fields = ['name', 'email', 'phone', 'subject', 'project__title']
    readonly_fields = ['created_at']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'created_at']
    list_editable = ['order']


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ['project', 'title', 'category', 'order', 'created_at']
    list_filter = ['category', 'created_at']
    list_editable = ['order']
    search_fields = ['project__title', 'title']


@admin.register(ProjectAmenity)
class ProjectAmenityAdmin(admin.ModelAdmin):
    list_display = ['project', 'name', 'icon', 'order', 'created_at']
    list_filter = ['created_at']
    list_editable = ['order']
    search_fields = ['project__title', 'name']


class TowerAmenityInline(admin.TabularInline):
    model = TowerAmenity
    extra = 1
    fields = ('name', 'icon', 'order')


class FlatInline(admin.TabularInline):
    model = Flat
    extra = 0
    fields = ('flat_number', 'flat_type', 'floor_number', 'carpet_area', 'price', 'status')
    readonly_fields = []


@admin.register(Tower)
class TowerAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'total_floors', 'total_flats', 'booking_status', 'is_active', 'order', 'created_at']
    list_filter = ['booking_status', 'is_active', 'created_at']
    search_fields = ['name', 'tower_number', 'project__title', 'rera_number']
    list_editable = ['is_active', 'order']
    inlines = [TowerAmenityInline, FlatInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'name', 'tower_number', 'booking_status', 'is_active', 'order')
        }),
        ('Tower Structure', {
            'fields': ('total_floors', 'parking_floors', 'residential_floors', 'refugee_floors', 'per_floor_flats', 'total_lifts', 'total_stairs'),
            'description': 'Total flats will be calculated automatically from the flats added to this tower'
        }),
        ('Dates & RERA', {
            'fields': ('start_date', 'completion_date', 'rera_completion_date', 'rera_number')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('project')


@admin.register(TowerAmenity)
class TowerAmenityAdmin(admin.ModelAdmin):
    list_display = ['tower', 'name', 'icon', 'order', 'created_at']
    list_filter = ['created_at']
    list_editable = ['order']
    search_fields = ['tower__name', 'tower__project__title', 'name']


@admin.register(Flat)
class FlatAdmin(admin.ModelAdmin):
    list_display = ['flat_number', 'tower', 'flat_type', 'floor_number', 'carpet_area', 'price', 'status', 'created_at']
    list_filter = ['flat_type', 'status', 'facing', 'balcony', 'parking', 'created_at']
    search_fields = ['flat_number', 'tower__name', 'tower__project__title']
    list_editable = ['status']
    fieldsets = (
        ('Basic Information', {
            'fields': ('tower', 'flat_number', 'flat_type', 'floor_number', 'status')
        }),
        ('Area Details', {
            'fields': ('carpet_area', 'built_up_area', 'super_area')
        }),
        ('Pricing', {
            'fields': ('price', 'price_per_sqft')
        }),
        ('Additional Details', {
            'fields': ('facing', 'balcony', 'parking', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('tower', 'tower__project')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'mobile', 'email', 'is_active', 'is_registered', 'last_login', 'created_at']
    list_filter = ['is_active', 'is_registered', 'created_at']
    search_fields = ['first_name', 'last_name', 'mobile', 'email']
    list_editable = ['is_active', 'is_registered']
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'mobile', 'email')
        }),
        ('Status', {
            'fields': ('is_active', 'is_registered')
        }),
        ('Timestamps', {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['mobile', 'otp_code', 'purpose', 'is_verified', 'expires_at', 'created_at']
    list_filter = ['purpose', 'is_verified', 'created_at']
    search_fields = ['mobile', 'otp_code']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

