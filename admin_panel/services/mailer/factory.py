from django.conf import settings

class Mailer:
  mail_classes = {}

  def register(self, mail_name, func):
    self.mail_classes[mail_name] = func

  def send_mail(self, mail_name, is_async=True, **kwargs):
    
    if not settings.ASYNC_EMAILS:
      is_async = False

    if mail_name not in self.mail_classes:
      print(f"Mail {mail_name} not registered")
      return

    if is_async:
      self.mail_classes[mail_name].delay(**kwargs)
    else:
      self.mail_classes[mail_name](**kwargs)

mailer = Mailer()