# Generated by Django 4.1.1 on 2024-01-29 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videos',
            name='urlstring',
            field=models.TextField(),
        ),
    ]
