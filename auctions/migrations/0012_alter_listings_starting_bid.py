# Generated by Django 5.0.3 on 2024-03-23 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_alter_listings_starting_bid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listings',
            name='starting_bid',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
    ]
