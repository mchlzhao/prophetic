from django import forms
from django.contrib.auth.models import User
from .models import Event, Group, Market, Order

class EventCreateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'group']
    
    def __init__(self, *args, **kwargs):
        group_id = kwargs.pop('group_id')
        super(EventCreateForm, self).__init__(*args, **kwargs)
        self.fields['group'].disabled = True
        self.fields['group'].initial = Group.objects.get(pk=group_id)
        self.fields['group'].widget = forms.HiddenInput()
    
    def save(self, created_by):
        e = super().save(commit=False)
        self.instance.created_by = created_by
        e.save()
