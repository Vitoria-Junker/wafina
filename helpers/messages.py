from django.utils.translation import ugettext_lazy as _

INVALID_CREDENTIALS_ERROR = _("Your credentials do not match.")
NON_REGISTERED_ACCOUNT = _("User does not exists")
INACTIVE_ACCOUNT_ERROR = _(
    'Your account is inactive. Please recover your password to activate your account.')
BLOCKED_ACCOUNT = _(
    'Your account is blocked for some reasons, please contact the admin')
INVALID_PHONENUMBER = _("Please enter valid phone number.")
INVALID_OTP = _("Invalid OTP. Please enter valid OTP.")
PHONE_NUMBER_VALIDATION_ERROR = _(
    "User with this mobile number does not exists")
CONTACT_NUMBER_VALIDATED = "Email verified"
UNREGISTERED_EMAIL = "No account is founded with this email id"
CONTACT_NUMBER_CHANGED = _("Contact number successfully changed")
CONTACT_NUMBER_ALREADY_EXISTS = _("This number is already in use")
WRONG_PASSWORD = _("Password is not correct")
PHONE_NUMBER_ALREADY_EXISTS = _("user with this contact number already exists.")
EMAIL_ALREADY_EXITS = 'User with this email address already exists.'
USERNAME_ALREADY_EXISTS = 'User with this username address already exists.'

OTP_SENT_SUCCESSFULLY = _("OTP resent successfully.")
