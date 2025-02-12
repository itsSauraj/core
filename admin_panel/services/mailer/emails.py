from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from admin_panel.services.TOTP import generate_otp_by_key, verify_otp_by_key

from admin_panel.models import User
from admin_panel.services.mailer.factory import mailer

def send_user_verification_email(user_id):
    user = User.objects.get(pk=user_id)

    mail_subject = 'Welcome to Abra, please verify your email address.'
    html_message = render_to_string('emails/signup-verification.html', {
        'user': user,
        'otp': generate_otp_by_key(user_id),
    })
    plain_message = strip_tags(html_message)
    send_mail(mail_subject, plain_message, settings.SENDER_EMAIL, [user.email],
                html_message=html_message)
    
def send_user_password_reset_email(user_id):
    user = User.objects.get(pk=user_id)

    mail_subject = 'Password reset | Abra'
    html_message = render_to_string('emails/forgot-password-reset.html', {
        'user': user,
        'otp': generate_otp_by_key(user_id),
    })
    plain_message = strip_tags(html_message)
    send_mail(mail_subject, plain_message, settings.SENDER_EMAIL, [user.email],
                html_message=html_message)
    
def send_user_password_changed_notification(user_id):
    user = User.objects.get(pk=user_id)

    mail_subject = 'Password reset | Scoop Investment'
    html_message = render_to_string('emails/password-changed.html', {
        'user': user,
        'date_time': str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    })
    plain_message = strip_tags(html_message)
    send_mail(mail_subject, plain_message, settings.SENDER_EMAIL, [user.email],
                html_message=html_message)
    
def send_user_account_deleted_notification(user_id):
    user = User.objects.get(pk=user_id)

    mail_subject = 'Password reset | Scoop Investment'
    html_message = render_to_string('emails/profile-deleted.html', {
        'user': user,
        'date_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    plain_message = strip_tags(html_message)
    send_mail(mail_subject, plain_message, settings.SENDER_EMAIL, [user.email],
                html_message=html_message)
    
def send_user_account_exam_scheduled_notification(user_id, exam):
    user = User.objects.get(pk=user_id)

    exam_details = {
        'name': exam.collection.title,
        'mentor': exam.assigned_mentor.first_name + ' ' + exam.assigned_mentor.last_name,
        'date_time': exam.exam_date.strftime('%Y-%m-%d %H:%M:%S') + ' ' + exam.exam_time.strftime('%H:%M:%S') + ' UTC',
        'scheduled_by': exam.created_by.first_name + ' ' + exam.created_by.last_name
    }

    mail_subject = 'Password reset | Scoop Investment'
    html_message = render_to_string('emails/exam-scheduled.html', {
        'user': user,
        'exam': exam_details
    })
    plain_message = strip_tags(html_message)
    send_mail(mail_subject, plain_message, settings.SENDER_EMAIL, [user.email],
                html_message=html_message)

def register_all():
    mailer.register('send_user_verification_email', send_user_verification_email)
    mailer.register('send_user_password_reset_email', send_user_password_reset_email)
    mailer.register('send_user_password_changed_notification', send_user_password_changed_notification)
    mailer.register('send_user_account_deleted_notification', send_user_account_deleted_notification)
    mailer.register('send_user_account_exam_scheduled_notification', send_user_account_exam_scheduled_notification)