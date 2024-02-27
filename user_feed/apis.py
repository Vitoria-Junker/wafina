from rest_framework import generics, permissions, status, response, parsers, exceptions, views, filters, viewsets
from .models import UserImage, UserLikesAndComment
from .serializers import UserUploadImagesSerializer, UserLikeAndDislikeSerializer, UserImageDataGetSerializer, \
    UserCommentsSerializer, CommentsDataSerializer, UserImageDataRetrieveSerializer
from django_filters import rest_framework as djfilters
from user_feed.utils.filters import FeedFilters
from accounts.models import User


class UploadImageAPI(viewsets.ModelViewSet):
    model = UserImage
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser,)
    filter_backends = (djfilters.DjangoFilterBackend,)
    filter_class = FeedFilters

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserUploadImagesSerializer
        elif self.request.method == 'GET' and not self.kwargs.get('pk'):
            return UserImageDataGetSerializer
        elif self.request.method == 'GET' and self.kwargs.get('pk'):
            return UserImageDataRetrieveSerializer
        else:
            return UserImageDataGetSerializer

    def get_serializer_context(self):
        return {'user_id': self.request.user.id,
                "request": self.request
                }

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if self.request.method == 'GET' and not self.kwargs.get('pk'):
            if user_id:
                return self.model.objects.filter(user_id=user_id,
                                                 is_active=True)
            else:
                raise exceptions.ValidationError(
                    "user_id is required in query parameters"
                )
        else:
            return self.model.objects.all()

    def list(self, request, *args, **kwargs):
        resp_dict = dict()
        user_id = request.query_params.get("user_id")
        user = User.objects.get_user_by_id(user_id=int(user_id))
        resp_dict["user_details"] = dict()
        resp_dict["user_details"]["full_name"] = user.full_name
        resp_dict["user_details"]["profile_picture"] = user.profile_picture.url if user.profile_picture else None
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer_class()
            serializer = serializer(queryset, many=True)
            resp_dict["data"] = serializer.data
        else:
            resp_dict["data"] = dict()
        return response.Response(
            resp_dict,
            status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            obj = serializer.save()
            obj.user = self.request.user
            obj.save()
            return response.Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class UserLikeActionAPI(generics.CreateAPIView):
    model = UserLikesAndComment
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserLikeAndDislikeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            image_id = serializer.validated_data["image_obj_id"]
            user = self.request.user
            image = UserImage.objects.filter(id=image_id).first()
            qs = self.model.objects.filter(image_obj_id=image_id,
                                           type_of_action='like').first()
            if not qs:
                extra_data = dict()
                extra_data["no_of_likes"] = 1
                extra_data["liked_by"] = [user.id]
                extra_data["disliked_by"] = []
                extra_data["no_of_dislikes"] = 0
                obj = self.model.objects.create(
                    image_obj=image,
                    likes_extra_data=extra_data,
                    type_of_action='like'
                )
                no_of_likes = obj.likes_extra_data["no_of_likes"]
                return response.Response(
                    {"no_of_likes": no_of_likes},
                    status=status.HTTP_201_CREATED
                )
            else:
                extra_data = qs.likes_extra_data
                if user.id in extra_data["liked_by"]:
                    extra_data["liked_by"].remove(user.id)
                    if extra_data["no_of_likes"] == 0:
                        extra_data["no_of_likes"] = 0
                    else:
                        extra_data["no_of_likes"] -= 1
                    extra_data["disliked_by"].append(user.id)
                    extra_data["no_of_dislikes"] += 1
                else:
                    extra_data["liked_by"].append(user.id)
                    extra_data["no_of_likes"] += 1
                    if user.id in extra_data["disliked_by"]:
                        extra_data["disliked_by"].remove(user.id)
                    if extra_data["no_of_dislikes"] == 0:
                        extra_data["no_of_dislikes"] = 0
                    else:
                        extra_data["no_of_dislikes"] -= 1
                qs.likes_extra_data = extra_data
                qs.save()
                no_of_likes = qs.likes_extra_data["no_of_likes"]
                return response.Response(
                    {"no_of_likes": no_of_likes},
                    status=status.HTTP_201_CREATED
                )
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class UserCommentsAPI(generics.CreateAPIView):
    serializer_class = UserCommentsSerializer
    model = UserLikesAndComment
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            image_id = serializer.validated_data["image_obj_id"]
            user = self.request.user
            image = UserImage.objects.filter(id=image_id).first()
            self.model.objects.create(
                image_obj=image,
                comment=serializer.validated_data["comment"],
                commented_by=user,
                type_of_action='comment'
            )
            return response.Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class LikesDataAPI(views.APIView):
    model = UserLikesAndComment
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        image_id = self.request.query_params.get("image_id")
        if image_id:
            return self.model.objects.filter(image_obj_id=image_id,
                                             type_of_action='like')
        else:
            raise exceptions.ValidationError(
                "image_id is required in query parameters"
            )

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        search = self.request.query_params.get("search", None)
        if queryset:
            qs = queryset.first()
            extra_data = qs.likes_extra_data
            user_ids = extra_data["liked_by"]
            if search:
                user_qs = User.objects.filter(id__in=user_ids,
                                              full_name__icontains=search)
            else:
                user_qs = User.objects.filter(id__in=user_ids)
            user_data_list = list()
            for obj in user_qs:
                if obj.profile_picture:
                    profile_picture = obj.profile_picture.url
                else:
                    profile_picture = None
                user_data_list.append(
                    {
                        "full_name": obj.full_name,
                        "profile_picture": profile_picture
                    }
                )
            return response.Response(
                user_data_list,
                status=status.HTTP_200_OK
            )
        else:
            return response.Response(
                [],
                status=status.HTTP_200_OK
            )


class CommentDataView(generics.ListAPIView):
    model = UserLikesAndComment
    serializer_class = CommentsDataSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('commented_by__full_name',)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        image_id = self.request.query_params.get("image_id")
        if image_id:
            return self.model.objects.filter(image_obj_id=image_id,
                                             type_of_action='comment')
        else:
            raise exceptions.ValidationError(
                "image_id is required in query parameters"
            )


