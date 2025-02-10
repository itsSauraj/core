import logging

from django.conf import settings


log = logging.getLogger(__name__)

class Mailer:
    mail_classes = {}

    def register(self, mail_name, func):
        self.mail_classes[mail_name] = func

    def send_mail(self, mail_name, is_async=True, **kwargs):
        if not settings.ASYNC_EMAILS:
            is_async = False

        if mail_name not in self.mail_classes:
            return

        if is_async:
            log.info(f"Sending mail async: {mail_name}")
            self.mail_classes[mail_name].delay(**kwargs)
        else:
            log.info(f"Sending mail sync: {mail_name}")
            self.mail_classes[mail_name](**kwargs)

mailer = Mailer()