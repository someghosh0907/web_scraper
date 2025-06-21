from django.db import models

class ScrapeJob(models.Model):
    scraper_name = models.CharField(max_length=100)
    website = models.CharField(max_length=50)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    min_year = models.IntegerField()
    max_year = models.IntegerField()
    city = models.CharField(max_length=50)
    fuel_type = models.CharField(max_length=20)
    transmission = models.CharField(max_length=20)
    frequency = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.scraper_name
