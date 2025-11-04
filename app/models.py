from django.db import models
from django.contrib.auth.models import User

# This BaseModel can be used to add common fields
class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Category(BaseModel):
    name = models.CharField(max_length=120, unique=True)
    VISIBILITY_CHOICES = [
        ("public", "Public"),
        ("private", "Private"),
    ]
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default="public")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'category'


class Tag(BaseModel):
    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'tag'


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.CharField(max_length=200, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    resume = models.FileField(upload_to="resumes/", null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    def __str__(self):
        return f"Profile({self.user.username})"
    
    class Meta:
        db_table = 'profile'


class Product(BaseModel):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.IntegerField()
    released_on = models.DateField()
    in_stock = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    tags = models.ManyToManyField(Tag, related_name="products", blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'product'



class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="product_images/")
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Image({self.product.name})"
    
    class Meta:
        db_table = 'productimage'