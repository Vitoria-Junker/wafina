from datetime import timedelta

from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
import pycountry
import time
from celery import Task

from helpers.notification_method import create_notification
from wafina_backend import celery_app
from helpers.emails import EmailMixin
from helpers.utils import get_stripe_client
from accounts.models import UserStripeVerification
from django.template.loader import get_template
from celery.task import periodic_task
from booking_requests.models import BookingSession


class SendOTPNotificationOnEmail(Task, EmailMixin):
    """sending opt to the respective user's registered e-mail"""

    name = "Email Notifications"
    subject_template_name = None
    html_body_template_name = None
    text_template = None

    def run(self, **ctx):
        self.subject_template_name = ctx.get('subject_template_name', None)
        self.html_body_template_name = ctx.get('html_body_template_name', None)
        self.text_template = ctx.get('text_template', None)

        self.create_email(**ctx)


celery_app.tasks.register(SendOTPNotificationOnEmail())


class StripeVerificationTask(Task):
    name = "Account Verification"

    def stripe_client(self):
        return get_stripe_client()

    def send_notifications(self, errors, email, full_name, domain_name):
        task = SendOTPNotificationOnEmail()
        if errors:
            ctx = {
                'user_email': email,
                'fullname': full_name,
                'errors': errors,
                'current_site': domain_name,
                'subject_template_name': 'Account can not be Approved',
                'html_body_template_name': get_template('account_incomplete.html').origin.name,
                'text_template': get_template('account_incomplete.txt').origin.name
            }

        else:
            ctx = {
                'user_email': email,
                'fullname': full_name,
                'current_site': domain_name,
                'subject_template_name': 'Account Creation Complete',
                'html_body_template_name': get_template('account_complete.html').origin.name,
                'text_template': get_template('account_complete.txt').origin.name
            }

        task.run(**ctx)

    def run(self, obj_id, domain_name):
        kyc = UserStripeVerification.objects.filter(id=obj_id)
        kyc_obj = UserStripeVerification.objects.filter(id=obj_id).first()
        user = kyc_obj.user
        stripe = self.stripe_client()
        name = user.full_name.split(" ")
        if len(name) == 2:
            first_name = name[0]
            last_name = name[1]
        else:
            first_name = user.full_name
            last_name = user.username
        try:
            back_photo_path = kyc_obj.document_back_picture.path
            front_photo_path = kyc_obj.document_front_picture.path
            country = pycountry.countries.get(name=user.country.name)
            currency = pycountry.currencies.get(numeric=country.numeric)
            with open(back_photo_path, "rb") as fp:
                back_stripe = stripe.File.create(
                    purpose="identity_document",
                    file=fp
                )
            with open(front_photo_path, "rb") as fp:
                front_stripe = stripe.File.create(
                    purpose="identity_document",
                    file=fp
                )
            with open(front_photo_path, "rb") as fp:
                address_proof_front_stripe = stripe.File.create(
                    purpose="identity_document",
                    file=fp
                )
            with open(back_photo_path, "rb") as fp:
                address_proof_back_stripe = stripe.File.create(
                    purpose="identity_document",
                    file=fp
                )
            stripe_account_obj = stripe.Account.create(
                type="custom",
                country=user.country,
                email=user.email,
                business_type='individual',
                individual={'address': {'city': user.city,
                                        'country': user.country,
                                        'postal_code': user.postcode,
                                        'line1': user.address,
                                        'line2': user.address
                                        },
                            'dob': {'day': user.date_of_birth.day,
                                    'month': user.date_of_birth.month,
                                    'year': user.date_of_birth.year},
                            'email': user.email,
                            'first_name': first_name,
                            'last_name': last_name,
                            'verification': {
                                'document': {
                                    'back': back_stripe.get('id'),
                                    'front': front_stripe.get('id')
                                },
                                'additional_document': {
                                    'back': address_proof_back_stripe.get('id'),
                                    'front': address_proof_front_stripe.get('id')
                                }
                            },
                            'phone': user.phone_number},

                business_profile={'product_description': "payment_gateway",
                                  'mcc': 7011},
                capabilities={
                    'card_payments':
                        {
                            "requested": True
                        },
                    "transfers":
                        {
                            "requested": True
                        },
                },
                tos_acceptance={
                    'date': int(time.time()),
                    'ip': '8.8.8.8',
                },
                external_account={'object': 'bank_account',
                                  'country': user.country.code,
                                  'currency': currency.alpha_3.lower(),
                                  'account_holder_name': user.full_name,
                                  'account_holder_type': 'individual',
                                  'routing_number': kyc_obj.bank_sort_code,
                                  'account_number': kyc_obj.bank_account_number},
            )
            kyc_obj.user.stripe_id = stripe_account_obj.stripe_id
            kyc_obj.user.account_complete = True
            kyc_obj.user.needs_action = False
            kyc_obj.user.save()
        except Exception as e:
            kyc_obj.errors.append(e.args[0])
            kyc_obj.save()
            kyc_obj.user.needs_action = True
            kyc_obj.user.save()
        errors = kyc_obj.errors
        self.send_notifications(errors=errors, email=user.email, full_name=user.full_name, domain_name=domain_name)
        if len(errors) != 0:
            kyc.delete()
            return
        else:
            return


celery_app.tasks.register(StripeVerificationTask())


@periodic_task(run_every=timedelta(minutes=5))
def send_notifications_for_review():
    time_now = timezone.now()
    session_qs = BookingSession.objects.filter(
        end_timestamp__lte=time_now,
        status="paid",
        reviewed=False
    )
    for qs in session_qs:
        name_list = list()
        for obj in qs.extra_data.get("requested_services_data"):
            name_list.append(obj['service_name'])
        notification_data = {
            "user_id": qs.source.id,
            "notification_subject": f'Share your Review',
            "notification_message": f"Tell us about your experience for the {','.join(name_list)} session with "
                                    f"{qs.target.full_name}",
            "session_id": qs.id,
            "actionable": True,
            "type_of_action": "post_review",
        }
        create_notification(notification_data)
        ctx = {
            "user_email": qs.source.email,
            "source_name": qs.source.full_name,
            "target_name": qs.target.full_name,
            "current_site": "wafina.co.uk",
            'subject_template_name': 'Share your Feedback',
            'html_body_template_name': 'post_review.html',
            'text_template': 'post_review.txt',
            'services': ','.join(name_list)
        }
        task = SendOTPNotificationOnEmail()
        task.run(**ctx)
        qs.reviewed = True
        qs.save()

