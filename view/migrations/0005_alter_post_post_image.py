# Generated by Django 4.2.1 on 2023-06-15 06:01

from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('view', '0004_rename_question_comment_post_comment_user_likepost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='post_image',
            field=django_resized.forms.ResizedImageField(crop=None, force_format='JPG', keep_meta=True, quality=80, scale=None, size=[500, 500], upload_to='images/'),
        ),
    ]
