# Generated by Django 3.1.7 on 2021-07-02 10:49

from django.db import migrations, models
import django_countries.fields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('full_name', models.CharField(blank=True, max_length=80, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('username', models.CharField(blank=True, max_length=20, null=True)),
                ('account_type', models.CharField(blank=True, choices=[('company', 'company'), ('freelancer', 'freelancer'), ('customer', 'customer')], max_length=30, null=True)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None, unique=True)),
                ('postcode', models.TextField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('city', models.CharField(blank=True, max_length=80, null=True)),
                ('experience', models.IntegerField(blank=True, null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_images/')),
                ('is_active', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
