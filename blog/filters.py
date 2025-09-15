import django_filters
from .models import Post


# custom filter for posts with date range support
class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    published_date__gte = django_filters.DateFilter(field_name='published_date', lookup_expr='gte')
    published_date__lte = django_filters.DateFilter(field_name='published_date', lookup_expr='lte')
    author__name = django_filters.CharFilter(field_name='author__name', lookup_expr='icontains')

    class Meta:
        model = Post
        fields = ['title', 'author__name', 'published_date__gte', 'published_date__lte']