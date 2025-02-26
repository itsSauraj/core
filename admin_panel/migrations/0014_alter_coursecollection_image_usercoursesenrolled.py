# Generated by Django 5.1.4 on 2025-01-20 10:47

import admin_panel.utils
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0013_coursecollection_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursecollection',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=admin_panel.utils.rename_file),
        ),
        migrations.CreateModel(
            name='UserCoursesEnrolled',
            fields=[
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('restored_at', models.DateTimeField(blank=True, null=True)),
                ('transaction_id', models.UUIDField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('enrolled_on', models.DateTimeField(auto_now_add=True, verbose_name='enrolled on')),
                ('started_on', models.DateTimeField(blank=True, null=True, verbose_name='started on')),
                ('completed_on', models.DateTimeField(blank=True, null=True, verbose_name='completed on')),
                ('completed', models.BooleanField(default=False, verbose_name='completed')),
                ('collection', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='enrolled_users', to='admin_panel.coursecollection')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrolled_courses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
