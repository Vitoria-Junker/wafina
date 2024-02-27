from rest_framework import serializers
from .models import UserImage, UserLikesAndComment


class UserUploadImagesSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        required=True,
        allow_null=False
    )
    extra_text = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True
    )

    class Meta:
        model = UserImage
        fields = ('image', 'extra_text')


class UserImageDataGetSerializer(serializers.ModelSerializer):
    no_of_likes = serializers.SerializerMethodField()
    no_of_comments = serializers.SerializerMethodField()
    photo_liked = serializers.SerializerMethodField()

    def get_photo_liked(self, obj):
        user_id = self.context.get("user_id")
        user_image = obj.user_image.filter(image_obj_id=obj.id,
                                           type_of_action='like'
                                           ).first()
        if user_image:
            extra_data = user_image.likes_extra_data
            if user_id in extra_data.get("liked_by"):
                return True
            else:
                return False
        else:
            return False

    def get_no_of_likes(self, obj):
        user_image = obj.user_image.filter(image_obj_id=obj.id,
                                           type_of_action='like'
                                           ).first()
        if user_image:
            extra_data = user_image.likes_extra_data
            if extra_data.get("no_of_likes"):
                return extra_data.get("no_of_likes")
            else:
                return 0
        else:
            return 0

    def get_no_of_comments(self, obj):
        comments_count = obj.user_image.filter(image_obj_id=obj.id,
                                               type_of_action='comment').count()
        return comments_count

    class Meta:
        model = UserImage
        fields = ('id', 'image', 'no_of_likes', 'no_of_comments', 'photo_liked', 'extra_text')


class UserImageDataRetrieveSerializer(serializers.ModelSerializer):
    no_of_likes = serializers.SerializerMethodField()
    no_of_comments = serializers.SerializerMethodField()
    photo_liked = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        try:
            return obj.user.full_name
        except:
            return None

    def get_photo_liked(self, obj):
        user_id = self.context.get("user_id")
        user_image = obj.user_image.filter(image_obj_id=obj.id,
                                           type_of_action='like'
                                           ).first()
        if user_image:
            extra_data = user_image.likes_extra_data
            if user_id in extra_data.get("liked_by"):
                return True
            else:
                return False
        else:
            return False

    def get_no_of_likes(self, obj):
        user_image = obj.user_image.filter(image_obj_id=obj.id,
                                           type_of_action='like'
                                           ).first()
        if user_image:
            extra_data = user_image.likes_extra_data
            if extra_data.get("no_of_likes"):
                return extra_data.get("no_of_likes")
            else:
                return 0
        else:
            return 0

    def get_no_of_comments(self, obj):
        comments_count = obj.user_image.filter(image_obj_id=obj.id,
                                               type_of_action='comment').count()
        return comments_count

    class Meta:
        model = UserImage
        fields = ('id', 'image', 'full_name', 'no_of_likes', 'no_of_comments', 'photo_liked', 'extra_text')


class UserLikeAndDislikeSerializer(serializers.ModelSerializer):
    image_obj_id = serializers.IntegerField(
        required=True,
        allow_null=False
    )

    class Meta:
        model = UserLikesAndComment
        fields = ('image_obj_id',)


class UserCommentsSerializer(serializers.ModelSerializer):
    image_obj_id = serializers.IntegerField(
        required=True,
        allow_null=False
    )
    comment = serializers.CharField(
        required=True,
        allow_null=False,
        allow_blank=False
    )

    class Meta:
        model = UserLikesAndComment
        fields = ('image_obj_id', 'comment')


class CommentsDataSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        if obj.commented_by:
            return obj.commented_by.full_name
        else:
            return None

    def get_profile_picture(self, obj):
        if obj.commented_by:
            if obj.commented_by.profile_picture:
                return obj.commented_by.profile_picture.url
            else:
                return None
        else:
            return None

    class Meta:
        model = UserLikesAndComment
        fields = ('full_name', 'profile_picture', 'comment')


