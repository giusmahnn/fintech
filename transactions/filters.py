import django_filters
from transactions.models import Transaction
from transactions.choices import Status, TransactionType


class TransactionFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(field_name="status", choices=Status.choices)
    transaction_type = django_filters.ChoiceFilter(field_name="transaction_type", choices=TransactionType.choices)
    year = django_filters.NumberFilter(method='filter_by_year')  
    month = django_filters.NumberFilter(method='filter_by_month') 
    class Meta:
        model = Transaction
        fields = ['status', 'date', 'transaction_type', 'year', 'month']

    def filter_by_year(self, queryset, name, value):
        if value:
            queryset = queryset.filter(date__year=value)
        return queryset

    def filter_by_month(self, queryset, name, value):
        if value:  
            queryset = queryset.filter(date__month=value)  
        return queryset