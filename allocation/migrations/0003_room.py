# Generated by Django 3.2.11 on 2022-01-14 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('allocation', '0002_student'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_number', models.CharField(max_length=20, unique=True)),
                ('roll_number', models.CharField(default='0', max_length=20)),
            ],
        ),
    ]