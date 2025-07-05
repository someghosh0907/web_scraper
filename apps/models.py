import uuid
from django.db import models

class CarQuery(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    scraper_name= models.CharField(max_length=100)
    car_make = models.CharField(max_length=100)
    car_model = models.CharField(max_length=100)
    website = models.CharField(max_length=100)
    country=models.CharField(max_length=50)
    city=models.CharField(max_length=50)
    status=models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.car_make} {self.car_model} ({self.website})"
    
    # class Meta:
    #     db_table = "carquery"

class CarListing(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    query = models.ForeignKey(CarQuery, on_delete=models.CASCADE, related_name='listings')
    image_url = models.URLField(max_length=500)
    make = models.CharField(max_length=100)       
    model = models.CharField(max_length=100) 
    trim = models.CharField(max_length=255, blank=True, null=True)
    currency = models.CharField(max_length=50)
    price = models.CharField(max_length=50,null=True, blank=True)
    mileage = models.CharField(max_length=50,null=True, blank=True)
    city = models.CharField(max_length=100)
    country= models.CharField(max_length=100)
    year = models.CharField(max_length=10)
    transmission = models.CharField(max_length=50,null=True, blank=True)
    fuel_type = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    vehicle_listing_date = models.CharField(max_length=50,null=True, blank=True)
    vehicle_exit_date = models.CharField(max_length=50, blank=True, null=True)
    seller_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    website = models.CharField(max_length=100)
    website_url=models.CharField(max_length=255)

    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"
    
    # class Meta:
    #     db_table = "carlisting"
