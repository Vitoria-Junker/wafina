from rest_framework import serializers
from .models import Conversation, Interactions


class ConversationSerializer(serializers.ModelSerializer):
    session_id = serializers.IntegerField(
        required=True,
        allow_null=False
    )
    message = serializers.CharField(
        required=False,
        allow_null=True
    )

    def validate_message(self, message):
        restricted_word = ["bank", "google", "gmail", "skype", "whatsapp", "mobile", "number", "account", "pay",
                           "payment"]
        if any(x in restricted_word for x in message.lower().split()):
            raise serializers.ValidationError(
                "Remember, never have your conversation outside of Wafina.Doing so may get your account restricted"
            )
        return message

    class Meta:
        model = Conversation
        fields = ("session_id", "message")


class ConversationListSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()
    session_name = serializers.SerializerMethodField()

    def get_session_name(self, obj):
        name_list = list()
        for val in obj.session.extra_data.get("requested_services_data"):
            name_list.append(val['service_name'])
        return name_list

    def get_sender_name(self, obj):
        sender_dict = dict()
        sender_dict["id"] = obj.sender.id
        sender_dict["full_name"] = obj.sender.full_name
        return sender_dict

    def get_receiver_name(self, obj):
        sender_dict = dict()
        sender_dict["id"] = obj.receiver.id
        sender_dict["full_name"] = obj.receiver.full_name
        return sender_dict

    class Meta:
        model = Conversation
        fields = ('sender_name', 'session_name', 'receiver_name', 'message', "created")


class InteractionSerializer(serializers.ModelSerializer):
    sender_info = serializers.SerializerMethodField()
    receiver_info = serializers.SerializerMethodField()

    def get_sender_info(self, obj):
        sender_dict = dict()
        sender_dict["id"] = obj.sender.id
        sender_dict["full_name"] = obj.sender.full_name
        if obj.sender.profile_picture:
            sender_dict["profile_picture"] = obj.sender.profile_picture.url
        else:
            sender_dict["profile_picture"] = None
        return sender_dict

    def get_receiver_info(self, obj):
        sender_dict = dict()
        sender_dict["id"] = obj.receiver.id
        sender_dict["full_name"] = obj.receiver.full_name
        if obj.receiver.profile_picture:
            sender_dict["profile_picture"] = obj.receiver.profile_picture.url
        else:
            sender_dict["profile_picture"] = None
        return sender_dict

    class Meta:
        model = Interactions
        fields = ("session_id", "sender_info", "receiver_info", "created_on")
