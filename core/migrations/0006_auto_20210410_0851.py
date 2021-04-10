# Generated by Django 3.0.3 on 2021-04-10 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_market_multiplier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='market',
            name='max_value',
            field=models.DecimalField(decimal_places=2, default=100, editable=False, max_digits=8),
        ),
        migrations.AlterField(
            model_name='market',
            name='min_value',
            field=models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=8),
        ),
        migrations.AlterField(
            model_name='market',
            name='multiplier',
            field=models.PositiveIntegerField(default=1, editable=False),
        ),
        migrations.AlterField(
            model_name='market',
            name='tick_size',
            field=models.DecimalField(decimal_places=2, default=1, editable=False, max_digits=8),
        ),
    ]
