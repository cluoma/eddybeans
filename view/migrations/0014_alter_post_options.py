# Generated by Django 4.2.2 on 2023-10-15 06:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('view', '0013_remove_video_slug'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'permissions': [('delete_own_post', 'Can delete their own post')]},
        ),
    ]
