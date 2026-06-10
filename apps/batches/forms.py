# apps/batches/forms.py

from django import forms
from .models import Batch, TastingNote

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

            # checklist
            'create_must_done', 'create_must_date',
            'pitch_yeast_done', 'pitch_yeast_date',
            'fo_24h_done', 'fo_24h_date',
            'fo_48h_done', 'fo_48h_date',
            'fo_72h_done', 'fo_72h_date',
            'fo_1_3_break_done', 'fo_1_3_break_date',
            'rack_secondary_done', 'rack_secondary_date',
            'bottled_done', 'bottled_date',
        ]
        widgets = {
            'batch_size':     forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'primary_date':   forms.DateInput(attrs={'type': 'date'}),
            'secondary_date': forms.DateInput(attrs={'type': 'date'}),
            'bottling_date':  forms.DateInput(attrs={'type': 'date'}),

            'create_must_date':      forms.DateInput(attrs={'type': 'date'}),
            'pitch_yeast_date':      forms.DateInput(attrs={'type': 'date'}),
            'fo_24h_date':           forms.DateInput(attrs={'type': 'date'}),
            'fo_48h_date':           forms.DateInput(attrs={'type': 'date'}),
            'fo_72h_date':           forms.DateInput(attrs={'type': 'date'}),
            'fo_1_3_break_date':     forms.DateInput(attrs={'type': 'date'}),
            'rack_secondary_date':   forms.DateInput(attrs={'type': 'date'}),
            'bottled_date':          forms.DateInput(attrs={'type': 'date'}),
        }


class TastingNoteForm(forms.ModelForm):
    class Meta:
        model = TastingNote
        fields = ['date', 'score', 'aroma', 'flavor', 'overall']
        widgets = {
            'date':    forms.DateInput(attrs={'type': 'date'}),
            'score':   forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'aroma':   forms.Textarea(attrs={'rows': 3}),
            'flavor':  forms.Textarea(attrs={'rows': 3}),
            'overall': forms.Textarea(attrs={'rows': 3}),
        }

