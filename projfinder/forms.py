from django import forms

from . import defaults

class ProjFinderForm(forms.Form):

    #TODO: Make this a custom field with only  valid values
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

    #location = form.CharField(
    #        label='Location',
    #        max_length=100,
    #        #initial=
    #        )

