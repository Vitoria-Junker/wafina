# Generated by Django 3.1.7 on 2021-08-15 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_feed', '0003_remove_userlikesandcomment_photo_liked'),
    ]

    operations = [
        migrations.AddField(
            model_name='userimage',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]