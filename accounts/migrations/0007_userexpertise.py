# Generated by Django 3.1.7 on 2021-07-23 10:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_user_date_of_birth'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserExpertise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('experience_in_years', models.PositiveIntegerField(blank=True, null=True)),
                ('cost_in_usd', models.PositiveIntegerField(blank=True, null=True)),
                ('expertise', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='admin_expertise', to='accounts.expertisemodel')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_expertise', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'User(s) Expertise Details',
            },
        ),
    ]
