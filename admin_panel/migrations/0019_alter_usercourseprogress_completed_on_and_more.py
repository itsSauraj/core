# Generated by Django 5.1.4 on 2025-01-22 06:30

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0018_usercourseprogress'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercourseprogress',
            name='completed_on',
            field=models.DateTimeField(auto_now_add=True, verbose_name='completed on'),
        ),
        migrations.CreateModel(
            name='UserCourseActivity',
            fields=[
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('restored_at', models.DateTimeField(blank=True, null=True)),
                ('transaction_id', models.UUIDField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('started_on', models.DateTimeField(auto_now_add=True, verbose_name='started on')),
                ('completed_on', models.DateTimeField(blank=True, null=True, verbose_name='completed on')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_activity', to='admin_panel.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_activity', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
