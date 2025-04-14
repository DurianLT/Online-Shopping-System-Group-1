# staff/forms.py
from django import forms

class AddTagForm(forms.Form):
    tag_name = forms.CharField(max_length=255, label="新标签", required=True)
