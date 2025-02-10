from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode

from admin_panel.models import User
from admin_panel.services.mailer.factory import mailer

def send_user_verification_email(user_id):
    user = User.objects.get(pk=user_id)

    mail_subject = 'Welcome to Scoop Investment, please verify your email address.'
    html_message = render_to_string('emails/signup-verification.html', {
        'user': user,
        'otp': 123456, #TODO: create otp generator
    })
    plain_message = strip_tags(html_message)
    send_mail(mail_subject, plain_message, settings.SENDER_EMAIL, [user.email],
                   html_message=html_message)

# def send_admin_verification_email(user_id):
#     user = User.objects.get(pk=user_id)

#     mail_subject = 'Welcome to Scoop Investment, please verify your email address.'
#     html_message = render_to_string('emails/signup-verification.html', {
#         'user': user,
#         'otp': 123456, #TODO: create otp generator
#     })
#     plain_message = strip_tags(html_message)
#     send_mail(mail_subject, plain_message, settings.SENDER_EMAIL, [user.email],
#                    html_message=html_message)
    
def send_user_password_reset_email(user_id):
    user = User.objects.get(pk=user_id)

    mail_subject = 'Password reset | Scoop Investment'
    html_message = render_to_string('emails/forgot-password-reset.html', {
        'user': user,
        'otp': 123456, #TODO: create otp generator
    })
    plain_message = strip_tags(html_message)
    send_mail(mail_subject, plain_message, settings.SENDER_EMAIL, [user.email],
                   html_message=html_message)

def register_all():
    mailer.register('send_user_verification_email', send_user_verification_email)
    mailer.register('send_user_password_reset_email', send_user_password_reset_email)