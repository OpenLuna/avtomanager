# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('narodna', '0002_postedimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReplacingBattery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='postedimage',
            name='theimage',
            field=models.ImageField(default=None, null=True, upload_to=b'/root/static/uploads/', blank=True),
        ),
    ]
