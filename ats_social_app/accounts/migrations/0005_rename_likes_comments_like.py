# Generated by Django 4.0.6 on 2022-08-29 11:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_comments_likes'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comments',
            old_name='likes',
            new_name='like',
        ),
    ]
