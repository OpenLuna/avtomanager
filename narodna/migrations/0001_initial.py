# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('unique_string', models.TextField(null=True, blank=True)),
                ('order', models.IntegerField(null=True, blank=True)),
                ('signup_time', models.DateTimeField(auto_now=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('end_time', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='EmailToSend',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField()),
                ('sent', models.BooleanField(default=False)),
                ('driver', models.ForeignKey(to='narodna.Driver')),
            ],
        ),
        migrations.CreateModel(
            name='Fura',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('end_time', models.DateTimeField(null=True, blank=True)),
                ('miliseconds', models.IntegerField(null=True, blank=True)),
                ('driver', models.ForeignKey(to='narodna.Driver')),
            ],
        ),
        migrations.CreateModel(
            name='Options',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('option1', models.BooleanField(default=False)),
                ('option2', models.BooleanField(default=False)),
                ('option3', models.BooleanField(default=False)),
                ('driver', models.ForeignKey(to='narodna.Driver')),
            ],
        ),
    ]
