# Generated by Django 4.2.1 on 2023-06-10 04:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_image', models.ImageField(upload_to='')),
                ('post_text', models.CharField(max_length=200)),
                ('post_date', models.DateTimeField(verbose_name='date')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_text', models.CharField(max_length=200)),
                ('comment_likes', models.IntegerField(default=0)),
                ('comment_date', models.DateTimeField(verbose_name='date')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='view.post')),
            ],
        ),
    ]