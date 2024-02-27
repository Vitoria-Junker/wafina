from django.db.models.query import QuerySet


class AccountQueryMixin(object):
    """ account  query mixin """

    def get_user_by_id(self, user_id):
        return self.get(id=user_id)

    def get_user_by_email(self, email):
        return self.get(email=email)

    def get_user_by_contact_number(self, phone_number):
        return self.get(phone_number=phone_number)


class AccountQuerySet(QuerySet, AccountQueryMixin):
    """ account query set """
    pass


class UserOtpQueryMixin(object):
    """ User otp query mixin"""

    def get_user_otp_by_otp_code(self, otp):
        return self.get(otp=otp)

    def get_otp_of_user(self, user):
        return self.get(user=user)

    def get_all_otp_of_user(self, user):
        return self.filter(user=user)

    def get_user_otp_by_otp_and_user(self, otp, user):
        return self.get(otp=otp, user=user)

    def get_user_otp_by_otp_and_contact(self, otp, contact_number):
        return self.get(otp=otp, phone_number=contact_number)


class UserOtpQuerySet(QuerySet, UserOtpQueryMixin):
    """UserOtp query set"""
    pass