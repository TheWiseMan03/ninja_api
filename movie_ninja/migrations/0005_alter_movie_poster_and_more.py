# Generated by Django 4.2.6 on 2023-10-25 06:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie_ninja', '0004_alter_actor_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='poster',
            field=models.CharField(max_length=200, verbose_name='Постер'),
        ),
        migrations.AlterField(
            model_name='token',
            name='access_token_expires_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 10, 25, 6, 4, 41, 734536, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='token',
            name='refresh_token_expires_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 10, 25, 6, 4, 41, 734536, tzinfo=datetime.timezone.utc)),
        ),
    ]
