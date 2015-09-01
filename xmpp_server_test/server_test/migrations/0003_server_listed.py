# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server_test', '0002_auto_20150828_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='listed',
            field=models.BooleanField(default=False),
        ),
    ]
