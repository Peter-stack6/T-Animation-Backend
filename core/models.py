from django.db import models
from django.contrib.auth.models import User

class FreeCourse(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    youtube_id = models.CharField(max_length=50)
    coin_reward = models.IntegerField()

class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    video_id = models.CharField(max_length=500, unique=True)
    price = models.IntegerField()
    coin_reward = models.IntegerField()

    def __str__(self):
        return self.title

class Resource(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    file = models.FileField(upload_to='resources/')
    money_price = models.IntegerField(default = 0)
    coin_price = models.IntegerField()

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    coins = models.IntegerField(default=0)
    has_ever_paid = models.BooleanField(default=False)
    
    bought_courses = models.ManyToManyField(Course, blank=True)
    bought_resources = models.ManyToManyField(Resource, blank=True)
    claimed_video_rewards = models.ManyToManyField(Course, blank=True, related_name='rewarded_profiles')

    def __str__(self):
        return f"Profile for {self.user.username}"
