# Generated by Django 3.1.7 on 2021-08-04 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_user_needs_action'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='needs_action',
            field=models.BooleanField(default=None, null=True),
        ),
    ]
