# Generated by Django 4.2.1 on 2023-06-10 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('view', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='post_image',
            field=models.ImageField(upload_to='images/'),
        ),
    ]
