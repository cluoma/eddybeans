from datetime import date

from django.db import models
from django.conf import settings
from django.db.models import UniqueConstraint
from imagefield.fields import ImageField


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    post_image = ImageField(
        upload_to='images/',
        formats={
            "full": ["default", ("thumbnail", (1280, 1280))],
            "thumbnail": ["default", ("thumbnail", (500, 500))],
            "superthumbnail": ["default", ("thumbnail", (100, 100))],
        },
        auto_add_fields=True,
        null=True
    )
    post_text = models.CharField(max_length=200)
    post_date = models.DateTimeField('date')
    post_day = models.DateField('day', default=date.today)
    post_day_order = models.PositiveSmallIntegerField(default=0)


    class Meta:
        permissions = [
            ("delete_own_post","Can delete their own post"),
            ("change_own_post","Can change their own post")
        ]

    def __str__(self):
        return self.post_text


class Video(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    video_file = models.FileField(upload_to='videos/%Y/%m/%d/', null=True, verbose_name="")
    video_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str('Video for post: ' + str(self.post_id))


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_text = models.CharField(max_length=200)
    comment_likes = models.IntegerField(default=0)
    comment_date = models.DateTimeField('date')

    def __str__(self):
        return self.comment_text


class LikePost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    like = models.BooleanField(default=True)

    class Meta:
        constraints = [UniqueConstraint("user", "post", name="unique_user_post")]

    def __str__(self):
        return str(self.like)

