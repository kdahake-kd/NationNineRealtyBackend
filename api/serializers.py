from rest_framework import serializers
from .models import (
    City, Project, Client, Review, BlogPost,
    Contact, Achievement,
    ProjectImage, ProjectAmenity, Tower, TowerAmenity, Flat, User, OTP
)


class ProjectImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectImage
        fields = '__all__'
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProjectAmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectAmenity
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class FlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flat
        fields = '__all__'


class TowerAmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = TowerAmenity
        fields = '__all__'


class TowerSerializer(serializers.ModelSerializer):
    flats = FlatSerializer(many=True, read_only=True)
    amenities = TowerAmenitySerializer(many=True, read_only=True)
    available_flats_count = serializers.SerializerMethodField()
    sold_flats_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tower
        fields = '__all__'
    
    def get_available_flats_count(self, obj):
        return obj.flats.filter(status='available').count()
    
    def get_sold_flats_count(self, obj):
        return obj.flats.filter(status='sold').count()


class ProjectSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()
    images = ProjectImageSerializer(many=True, read_only=True)
    amenities = ProjectAmenitySerializer(many=True, read_only=True)
    towers = TowerSerializer(many=True, read_only=True)
    city_name_display = serializers.SerializerMethodField()
    towers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = '__all__'
    
    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url
        return None
    
    def get_city_name_display(self, obj):
        return obj.get_city_name()
    
    def get_towers_count(self, obj):
        return obj.towers.count()


class ClientSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = '__all__'
    
    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class BlogPostSerializer(serializers.ModelSerializer):
    featured_image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = '__all__'
    
    def get_featured_image_url(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
        return None
    
    def get_video_url(self, obj):
        if obj.video:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video.url)
            return obj.video.url
        return None


class ContactSerializer(serializers.ModelSerializer):
    project_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ['read', 'created_at']
    
    def get_project_title(self, obj):
        return obj.project.title if obj.project else None


class AchievementSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Achievement
        fields = '__all__'
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'mobile', 'is_active', 'is_admin', 'created_at']
        read_only_fields = ['id', 'created_at']


class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['mobile', 'otp_code', 'purpose', 'is_verified']
        read_only_fields = ['is_verified']

