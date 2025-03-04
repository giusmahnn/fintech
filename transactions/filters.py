import django_filters
from transactions.models import Transaction
from transactions.choices import Status, TransactionType
from django.db.models import Sum


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

    def get_summary(self): 
        queryset = self.qs  
        total_in = queryset.filter().aggregate(Sum('amount'))['amount__sum'] or 0  
        total_out = queryset.filter().aggregate(Sum('amount'))['amount__sum'] or 0  

        return {  
            'In': total_in,  
            'Out': total_out
        }  