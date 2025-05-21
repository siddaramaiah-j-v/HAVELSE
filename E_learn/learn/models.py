from django.db import models
from django.utils.text import slugify
from django.urls import reverse



class Course(models.Model):
    title = models.CharField(max_length=200)
    subtitle=models.CharField(max_length=500,blank=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('tutorial:course', args=[self.slug])

    # def get_sections(self):
        # return self.section_set.all().order_by('order')


class Section(models.Model):
    """Main sections of a course (like chapters)"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        ordering = ['order']
        unique_together = ['course','order']



class Languages(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name='languages')
    language=models.CharField(max_length=20)

    def __str__(self):
        return f"{self.course.title}-{self.language}"

class Playlists(models.Model):
    title=models.ForeignKey(Languages,on_delete=models.CASCADE,related_name='playlists')
    list_id=models.CharField(max_length=100)

    def __str__(self):
        return f"{self.title.language}-{self.list_id}"