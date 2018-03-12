from django.db import models

# Create your models here.

class Tweet(models.Model):
    user = models.CharField(max_length=50, default=None)
    fullname = models.CharField(max_length=100)
    tweet_id = models.IntegerField()
    url = models.CharField(max_length=200)
    timestamp = models.DateTimeField();
    text = models.CharField(max_length=300)
    replies = models.IntegerField()
    retweets = models.IntegerField()
    likes = models.IntegerField()
    hashtags = models.CharField(max_length=200)
    tweet_class = models.IntegerField(null=True, default=None)

    def __str__(self):
        return self.user + ": " + self.text
