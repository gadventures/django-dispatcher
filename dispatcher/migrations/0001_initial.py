# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.CharField(max_length=30)),
                ('chain_type', models.CharField(max_length=30)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_modified', models.DateField(auto_now=True)),
                ('date_next_update', models.DateField(auto_now=True)),
                ('disabled', models.BooleanField(default=False)),
                ('is_locked', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ChainEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('action', models.CharField(max_length=30)),
                ('value', models.CharField(max_length=30)),
                ('chain', models.ForeignKey(related_name='chain_event', to='dispatcher.Chain')),
                ('requested_by', models.CharField(max_length=30, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ChainResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('resource_id', models.CharField(max_length=30)),
                ('resource_type', models.CharField(max_length=30)),
                ('chain', models.ForeignKey(related_name='chain_resources', to='dispatcher.Chain')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='ChainResource',
            unique_together=(('chain', 'resource_id', 'resource_type'), ),
        ),
    ]
