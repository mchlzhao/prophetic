# Generated by Django 3.0.3 on 2021-04-17 12:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_market_event'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='description',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='event',
            name='details',
        ),
    ]