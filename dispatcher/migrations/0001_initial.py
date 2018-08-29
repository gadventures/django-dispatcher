# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MessageChain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.CharField(max_length=30)),
                ('chain_type', models.CharField(max_length=30)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_modified', models.DateField(auto_now=True)),
                ('date_next_update', models.DateField(auto_now=True)),
                ('last_requested_by', models.CharField(max_length=30)),
                ('disabled', models.NullBooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='MessageChainEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('action', models.CharField(max_length=30)),
                ('value', models.CharField(max_length=30)),
                ('chain', models.ForeignKey(related_name='chain_event', to='dispatcher.MessageChain')),
            ],
        ),
        migrations.CreateModel(
            name='MessageChainResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('resource_id', models.CharField(max_length=30)),
                ('resource_type', models.CharField(max_length=30)),
                ('chain', models.ForeignKey(related_name='chain_resources', to='dispatcher.MessageChain')),
            ],
        ),
    ]
