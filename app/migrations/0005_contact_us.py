# Generated by Django 4.1.5 on 2023-02-20 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_user_info_otp'),
    ]

    operations = [
        migrations.CreateModel(
            name='contact_us',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(blank=True, max_length=250, null=True)),
                ('subject', models.CharField(blank=True, max_length=250, null=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('status', models.BooleanField(default=False)),
                ('added_on', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Contact Us Table',
            },
        ),
    ]