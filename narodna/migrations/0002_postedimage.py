# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('narodna', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='postedImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('thetitle', models.CharField(max_length=255)),
                ('theimage', models.ImageField(default=None, null=True, upload_to=b'/root/static/', blank=True)),
            ],
        ),
    ]
