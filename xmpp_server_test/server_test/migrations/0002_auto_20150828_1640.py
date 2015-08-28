# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('server_test', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='servertest',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 28, 16, 40, 14, 542055), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servertest',
            name='finished',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='servertest',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 28, 16, 40, 19, 717145), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='servertest',
            name='data',
            field=jsonfield.fields.JSONField(default={}, blank=True),
        ),
    ]
