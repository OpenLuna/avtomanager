# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('narodna', '0004_fura_session_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='fura',
            name='last_seen',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='fura',
            name='session_id',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
    ]
