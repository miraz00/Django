# Generated by Django 4.2.5 on 2023-09-11 14:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_alter_auctionlistings_current_bid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlistings',
            name='category',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='auctionlistings',
            name='current_bid',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='auctionlistings',
            name='description',
            field=models.CharField(max_length=5000, null=True),
        ),
        migrations.AlterField(
            model_name='auctionlistings',
            name='url',
            field=models.URLField(null=True),
        ),
    ]
