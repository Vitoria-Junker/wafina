from notifications.models import InAppNotification


def create_notification(data):
    InAppNotification.objects.create(**data)
    return
