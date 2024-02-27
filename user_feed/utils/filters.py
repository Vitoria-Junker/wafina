import django_filters
from ..models import UserImage


class FeedFilters(django_filters.FilterSet):
    user_id = django_filters.Filter(method='filter_user')

    class Meta:
        model = UserImage
        fields = ('is_active',)

    def filter_user(self, queryset, name, user_id):
        return queryset.filter(user_id=user_id)

