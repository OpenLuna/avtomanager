# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('narodna', '0003_auto_20160310_1354'),
    ]

    operations = [
        migrations.AddField(
            model_name='fura',
            name='session_id',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
    ]
