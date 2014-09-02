# -*- coding: utf-8 -*-
import operator

from django import forms
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.forms.forms import DeclarativeFieldsMetaclass
from django.utils import six


class FormOptions(object):
    def __init__(self, options=None):
        self.filters = getattr(options, 'filters', None)
        self.distinct = getattr(options, 'distinct', False)
        self.order = getattr(options, 'order', None)


class DeclarativeMetaclass(DeclarativeFieldsMetaclass):
    def __new__(mcs, *args):
        new_class = super(DeclarativeMetaclass, mcs).__new__(mcs, *args)
        new_class._meta = FormOptions(getattr(new_class, 'Meta', None))

        return new_class


class QueryForm(six.with_metaclass(DeclarativeMetaclass, forms.BaseForm)):

    def __init__(self, data=None, objects_per_page=None, **kwargs):
        super(QueryForm, self).__init__(data, **kwargs)
        self.objects_per_page = objects_per_page

    def get_filter(self):
        opts = self._meta
        result = []
        for field_name, value in self.cleaned_data.items():
            q_list = []
            if value:
                q_filter = opts.filters.get(field_name, None)
                if not isinstance(q_filter, (list, tuple)):
                    q_filter = [q_filter]
                q_list = [Q(**{q: value}) for q in q_filter]

            q_filter = reduce(operator.or_, q_list) if q_list else None

            if q_filter:
                result.append(q_filter)

        return reduce(operator.and_, result) if result else None

    def paginate(self, queryset):
        paginator = Paginator(queryset, self.objects_per_page)

        page = self.data.get('page')
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            queryset = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page of results.
            queryset = paginator.page(paginator.num_pages)

        return queryset

    def order(self, queryset):
        opts = self._meta
        order_by = self.data.get('order_by')

        if order_by and opts.order:
            order_query = opts.order.get(order_by.lstrip('-'))

            if order_query:
                order_query = '-' + order_query if order_by.startswith('-') else order_query
                queryset = queryset.order_by(order_query)

        return queryset

    def apply(self, queryset):
        query = self.get_filter()
        if query:
            if self._meta.distinct:
                queryset = queryset.distinct()
            queryset = queryset.filter(query)

        queryset = self.order(queryset)

        if self.objects_per_page:
            queryset = self.paginate(queryset)

        return queryset
