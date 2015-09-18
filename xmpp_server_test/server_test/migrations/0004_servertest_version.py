# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server_test', '0003_server_listed'),
    ]

    operations = [
        migrations.AddField(
            model_name='servertest',
            name='version',
            field=models.IntegerField(default=0),
        ),
    ]
