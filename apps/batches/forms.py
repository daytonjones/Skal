# apps/batches/forms.py

from django import forms
from .models import Batch

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = [
            'recipe',
            'name',
            'batch_size',
            'og',
            'fg',
            'primary_date',
            'secondary_date',
            'bottling_date',
            'notes',
            'is_public',
        ]
        widgets = {
            'batch_size':     forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'primary_date':   forms.DateInput(attrs={'type': 'date'}),
            'secondary_date': forms.DateInput(attrs={'type': 'date'}),
            'bottling_date':  forms.DateInput(attrs={'type': 'date'}),
        }

