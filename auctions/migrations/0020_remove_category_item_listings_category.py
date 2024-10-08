# Generated by Django 5.0.3 on 2024-03-30 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0019_alter_listings_starting_bid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='item',
        ),
        migrations.AddField(
            model_name='listings',
            name='category',
            field=models.ManyToManyField(blank=True, related_name='categories', to='auctions.category'),
        ),
    ]
