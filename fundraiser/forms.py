from django import forms

class AmountForm(forms.Form):
    amount = forms.CharField(max_length=254, required=True)
