from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_next_link(self):
        if not self.page.has_next():
            return None
        return self.request.build_absolute_uri().replace(f'page={self.page.number}', f'page={self.page.next_page_number()}')

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        return self.request.build_absolute_uri().replace(f'page={self.page.number}', f'page={self.page.previous_page_number()}')

    def paginate_queryset(self, queryset, request, view=None):
        self.page_size = request.query_params.get(self.page_size_query_param, self.page_size)
        self.page_size = min(int(self.page_size), self.max_page_size)
        self.request = request
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'page_size': self.page_size,
            'page': self.page.number,
            'results': data
        })