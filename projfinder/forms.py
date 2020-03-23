from django import forms

class ProjFinderForm(forms.Form):

    min_grade = forms.CharField(label='Maximum Grade', max_length=6)

