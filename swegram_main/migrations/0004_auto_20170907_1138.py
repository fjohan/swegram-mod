# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-07 09:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swegram_main', '0003_uploadedtext'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UploadedText',
            new_name='UploadedFile',
        ),
    ]
