# Generated by Django 5.0.3 on 2024-04-06 03:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0021_alter_watchlist_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='listings',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
