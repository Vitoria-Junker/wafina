from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template import loader
from django.conf import settings
from datetime import datetime


class EmailMixin(object):
    name = None
    subject_template_name = None
    html_body_template_name = None
    text_template = None
    cc = []

    def create_email(self, **ctx):
        try:
            subject = loader.render_to_string(self.subject_template_name, ctx)
            subject = ''.join(subject.splitlines())
        except:
            subject = ctx.get('subject_template_name')

        try:
            html_body = loader.render_to_string(self.html_body_template_name, ctx)
        except:
            html_body = ctx.get('html_body_template_name')
        text_body = loader.render_to_string(self.text_template, ctx)
        cc = ctx['cc'] if ctx.get('cc') else []

        msg = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL,  [ctx['user_email']],
                                     cc=cc)
        msg.attach_alternative(html_body, 'text/html')
        msg.send()
