from django import forms

from . import defaults

class ProjFinderForm(forms.Form):

    min_grade = forms.CharField(
            label='Grade', 
            max_length=6, 
            initial=defaults.MIN_GRADE,
            )
    max_distance = forms.DecimalField(
            label='Distance', 
            max_digits=6, 
            decimal_places=0, 
            initial=defaults.MAX_DISTANCE)

