# Generated by Django 4.1.6 on 2023-02-13 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('sub_id', models.CharField(max_length=255, null=True)),
                ('social_acc', models.CharField(max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
