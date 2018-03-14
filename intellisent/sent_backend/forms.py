from django import forms

class ScrapeForm(forms.Form):
    query = forms.CharField(label='Query')
    choices = (
        ('1', '500'),
        ('2', '2000'),
        ('3', '10000')
    )
    num = forms.ChoiceField(choices=choices)
