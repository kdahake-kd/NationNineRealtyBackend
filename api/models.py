from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class ClientUser(models.Model):
    """Custom User model for mobile-based authentication (Normal Users)"""
    first_name = models.CharField(max_length=100, blank=True, default='')
    last_name = models.CharField(max_length=100, blank=True, default='')
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=True)
    is_registered = models.BooleanField(default=False)  # True after user completes profile
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.first_name:
            return f"{self.first_name} {self.last_name} - {self.mobile}"
        return f"User - {self.mobile}"
        
class City(models.Model):
    """City model for admin to add cities"""
    name = models.CharField(max_length=100, unique=True)
    state = models.CharField(max_length=100, default='Maharashtra')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Cities'
    
    def __str__(self):
        return self.name


class Project(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('resale', 'Resale'),
    ]
    
    # Project Status choices (for search)
    PROJECT_STATUS_CHOICES = [
        ('pre_launch', 'Pre Launch'),
        ('new_launch', 'New Launch'),
        ('new_tower_launch', 'New Tower Launch'),
        ('ready_to_move', 'Ready To Move'),
        ('nearing_possession', 'Nearing Possession'),
    ]
    
    # Flat Type choices (available in project)
    FLAT_TYPE_CHOICES = [
        ('1bhk', '1 BHK'),
        ('1.5bhk', '1.5 BHK'),
        ('2bhk', '2 BHK'),
        ('2.5bhk', '2.5 BHK'),
        ('3bhk', '3 BHK'),
        ('3.5bhk', '3.5 BHK'),
        ('4bhk', '4 BHK'),
        ('4.5bhk', '4.5 BHK'),
        ('5bhk', '5 BHK'),
        ('5.5bhk', '5.5 BHK'),
    ]
    
    title = models.CharField(max_length=200)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    transaction_type = models.CharField(max_length=10, default='buy', help_text='All projects are for Buy only')
    is_hot = models.BooleanField(default=False, help_text='Mark as Hot property')
    
    # Project status field
    project_status = models.CharField(max_length=30, choices=PROJECT_STATUS_CHOICES, blank=True, null=True)
    available_flat_types = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text='Comma-separated flat types: 1bhk,2bhk,3bhk'
    )
    
    location = models.CharField(max_length=200)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')
    city_name = models.CharField(max_length=100, default='Pune', help_text='Fallback if city FK is null')
    state = models.CharField(max_length=100, default='Maharashtra')
    description = models.TextField()
    cover_image = models.ImageField(upload_to='projects/')
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    views = models.IntegerField(default=0)
    featured = models.BooleanField(default=False)
    
    # Additional Details
    id_number = models.CharField(max_length=50, blank=True, null=True)
    about_listing = models.TextField(blank=True, null=True)
    map_location = models.TextField(blank=True, null=True)  # Full address for map
    
    # Project Details (like RERA, area, etc.)
    rera_number = models.CharField(max_length=100, blank=True, null=True)
    land_area = models.CharField(max_length=100, blank=True, null=True, help_text='e.g., 2.2 ACRES')
    amenities_area = models.CharField(max_length=100, blank=True, null=True, help_text='e.g., 25K SQ FT')
    total_units = models.IntegerField(blank=True, null=True)
    total_towers = models.IntegerField(blank=True, null=True)
    developer_name = models.CharField(max_length=200, blank=True, null=True)
    
    # Specifications
    structure = models.CharField(max_length=200, blank=True, null=True)
    flooring = models.TextField(blank=True, null=True)
    kitchen = models.TextField(blank=True, null=True)
    electrical = models.TextField(blank=True, null=True)
    doors = models.TextField(blank=True, null=True)
    plaster = models.TextField(blank=True, null=True)
    windows = models.TextField(blank=True, null=True)
    toilet = models.TextField(blank=True, null=True)
    security_safety = models.TextField(blank=True, null=True)
    paint = models.TextField(blank=True, null=True)
    plumbing = models.TextField(blank=True, null=True)
    lift = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_city_name(self):
        """Get city name from FK or fallback"""
        return self.city.name if self.city else self.city_name


class Client(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='clients/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Review(models.Model):
    customer_name = models.CharField(max_length=200)
    designation = models.CharField(max_length=200, default='Happy Customer')
    review_text = models.TextField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer_name} - {self.rating} stars"


class BlogPost(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='blog_posts', blank=True, null=True, help_text='Related project for this blog post')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField(max_length=500)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    video = models.FileField(upload_to='blog/videos/', blank=True, null=True, help_text='Video file for project walkthrough')
    author = models.CharField(max_length=100, default='NationNineRealty')
    category = models.CharField(max_length=100, default='Real Estate')
    views = models.IntegerField(default=0)
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Contact(models.Model):
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, related_name='contacts', blank=True, null=True, help_text='Project the customer is interested in')
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

class ProjectEnquiry(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='Enquiries',help_text='Project Specific Enquiry')
    user = models.ForeignKey(ClientUser, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=20)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class Achievement(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='achievements/')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    IMAGE_CATEGORY_CHOICES = [
        ('inside_view', 'Inside View'),
        ('left_view', 'Left View'),
        ('right_view', 'Right View'),
        ('front_view', 'Front View'),
        ('back_view', 'Back View'),
        ('amenity', 'Amenity'),
        ('gym', 'Gym'),
        ('lawn', 'Lawn'),
        ('pool', 'Pool'),
        ('playground', 'Playground'),
        ('lobby', 'Lobby'),
        ('other', 'Other'),
    ]
    
    project = models.ForeignKey(Project, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='projects/gallery/')
    title = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=50, choices=IMAGE_CATEGORY_CHOICES, default='other')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.project.title} - {self.get_category_display()}"


class ProjectAmenity(models.Model):
    project = models.ForeignKey(Project, related_name='amenities', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    icon = models.CharField(max_length=100, blank=True)  # For emoji or icon class
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Project Amenities'
    
    def __str__(self):
        return f"{self.project.title} - {self.name}"


class Tower(models.Model):
    """Tower model - belongs to a Project"""
    project = models.ForeignKey(Project, related_name='towers', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text='e.g., A, B, C or Tower 1, Tower 2')
    tower_number = models.CharField(max_length=50, blank=True, null=True, help_text='e.g., A Wing, B Wing')
    
    # Tower Details
    total_floors = models.IntegerField(default=0)
    parking_floors = models.IntegerField(default=0)
    residential_floors = models.IntegerField(default=0)
    refugee_floors = models.IntegerField(default=0, help_text='Refuge floors')
    per_floor_flats = models.IntegerField(default=0)
    total_lifts = models.IntegerField(default=0)
    total_stairs = models.IntegerField(default=0)
    
    # Dates
    start_date = models.DateField(blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    rera_completion_date = models.DateField(blank=True, null=True)
    rera_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    booking_status = models.CharField(
        max_length=50,
        choices=[
            ('booking_open', 'Booking Open'),
            ('booking_closed', 'Booking Closed'),
            ('sold_out', 'Sold Out'),
        ],
        default='booking_open'
    )
    
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        unique_together = ['project', 'name']
    
    def __str__(self):
        return f"{self.project.title} - {self.name}"
    
    @property
    def total_flats(self):
        """Calculate total flats from related flats"""
        return self.flats.count()


class TowerAmenity(models.Model):
    """Amenities specific to a Tower"""
    tower = models.ForeignKey(Tower, related_name='amenities', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    icon = models.CharField(max_length=100, blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Tower Amenities'
    
    def __str__(self):
        return f"{self.tower.name} - {self.name}"


class Flat(models.Model):
    """Flat model - belongs to a Tower"""
    FLAT_TYPE_CHOICES = [
        ('1bhk', '1 BHK'),
        ('1.5bhk', '1.5 BHK'),
        ('2bhk', '2 BHK'),
        ('2.5bhk', '2.5 BHK'),
        ('3bhk', '3 BHK'),
        ('3.5bhk', '3.5 BHK'),
        ('4bhk', '4 BHK'),
        ('4.5bhk', '4.5 BHK'),
        ('5bhk', '5 BHK'),
        ('5.5bhk', '5.5 BHK'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('reserved', 'Reserved'),
        ('hold', 'Hold'),
    ]
    
    tower = models.ForeignKey(Tower, related_name='flats', on_delete=models.CASCADE)
    flat_number = models.CharField(max_length=50, help_text='e.g., A-101, B-201')
    flat_type = models.CharField(max_length=20, choices=FLAT_TYPE_CHOICES)
    floor_number = models.IntegerField()
    
    # Area details
    carpet_area = models.DecimalField(max_digits=10, decimal_places=2, help_text='Carpet area in SQFT')
    built_up_area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text='Built-up area in SQFT')
    super_area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text='Super area in SQFT')
    
    # Pricing
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    price_per_sqft = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Additional details
    facing = models.CharField(max_length=50, blank=True, null=True, help_text='e.g., North, South, East, West')
    balcony = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['floor_number', 'flat_number']
        unique_together = ['tower', 'flat_number']
    
    def __str__(self):
        return f"{self.tower.name} - {self.flat_number} ({self.get_flat_type_display()})"





class OTP(models.Model):
    """OTP model for mobile verification"""
    mobile = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    purpose = models.CharField(
        max_length=20,
        choices=[
            ('signup', 'Sign Up'),
            ('login', 'Login'),
            ('contact', 'Contact Form'),
        ],
        default='login'
    )
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['mobile', 'otp_code']),
        ]
    
    def __str__(self):
        return f"{self.mobile} - {self.otp_code}"

