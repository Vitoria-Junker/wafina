# Generated by Django 3.1.7 on 2021-08-04 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_user_personal_info_added'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='needs_action',
            field=models.NullBooleanField(default=None),
        ),
    ]
