from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, null=True, blank=True)
    pub_date = models.DateTimeField()
    host = models.TextField()  # This can store a list of hosts as a comma-separated string or JSON
    link = models.URLField(max_length=500)
    picture_link = models.URLField(max_length=500, null=True, blank=True)
    event_description = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=500)
    categories = models.TextField()  # This can store a list of categories as a comma-separated string or JSON

    def __str__(self):
        return self.title
