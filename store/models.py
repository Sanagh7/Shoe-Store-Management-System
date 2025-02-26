from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Shoe(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    description = models.TextField(blank=True)
    
    # Enhanced image fields
    image = models.ImageField(upload_to='shoe_images/', blank=True, null=True)
    image_name = models.CharField(max_length=255, blank=True)
    image_size = models.IntegerField(null=True, blank=True)
    image_type = models.CharField(max_length=50, blank=True)
    image_width = models.IntegerField(null=True, blank=True)
    image_height = models.IntegerField(null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.image:
            # Update image metadata
            self.image_name = self.image.name
            self.image_size = self.image.size
            self.image_type = self.image.content_type if hasattr(self.image, 'content_type') else ''
            
            # Get image dimensions
            try:
                from PIL import Image
                img = Image.open(self.image)
                self.image_width, self.image_height = img.size
            except Exception as e:
                print(f"Error processing image: {e}")
                
        super().save(*args, **kwargs)

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.shoe.price * self.quantity

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  # 'login' or 'logout'
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'User Activities'

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"