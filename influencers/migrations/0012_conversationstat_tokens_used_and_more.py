# Generated by Django 5.2.1 on 2025-06-27 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('influencers', '0011_conversationstat'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversationstat',
            name='tokens_used',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='conversationstat',
            name='tts_credits_used',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
