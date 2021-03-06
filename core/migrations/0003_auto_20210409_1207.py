# Generated by Django 3.0.3 on 2021-04-09 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20210409_1107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='market',
            name='max_value',
            field=models.DecimalField(decimal_places=2, default=100, max_digits=8),
        ),
        migrations.AlterField(
            model_name='market',
            name='min_value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AlterField(
            model_name='market',
            name='tick_size',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=8),
        ),
    ]
