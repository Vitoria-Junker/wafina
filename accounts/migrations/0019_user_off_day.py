# Generated by Django 3.1.7 on 2021-10-02 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_auto_20210906_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='off_day',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
    ]
