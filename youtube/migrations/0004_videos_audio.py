# Generated by Django 4.1.1 on 2024-01-30 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0003_remove_videos_urlstring_videos_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='videos',
            name='audio',
            field=models.FileField(default='', upload_to='audio'),
        ),
    ]
