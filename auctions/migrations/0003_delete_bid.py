# Generated by Django 5.0.3 on 2024-03-22 01:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_listings_starting_bid_bid'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Bid',
        ),
    ]
