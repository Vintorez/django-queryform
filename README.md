=========
QueryForm
=========

QueryForm is a simple Django app to filter querysets.

##Quick start


1. Add "queryform" to your INSTALLED_APPS setting like this:
```
    INSTALLED_APPS = (
        ...
        "queryform",
    )
```

###Usage

1. Create custom based on QueryForm;
2. Add filter input fields with widgets and attributes;
3. Set filter parameters;

```
    from queryform import QueryForm
    
    class CustomQueryForm(QueryForm):
        full_name_or_email = forms.CharField(required=False, widget=forms.TextInput())
        timestamp = forms.DateField(required=False, widget=forms.TextInput())
        
        class Meta:
            distinct = True
            filters = {
                'full_name_or_email': [
                    'user__first_name__icontains',
                    'user__last_name__icontains',
                    'user__email__icontains'
                ],
                'timestamp': 'timestamp__gte',
            }
```
