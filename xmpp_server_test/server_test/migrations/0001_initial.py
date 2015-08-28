# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('domain', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ServerTest',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('data', jsonfield.fields.JSONField(default={})),
                ('server', models.ForeignKey(to='server_test.Server', related_name='tests')),
            ],
        ),
    ]
