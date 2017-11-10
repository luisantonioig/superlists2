from django import forms
from lists.models import Item

class ItemForm(forms.models.ModelForm):
    EMPTY_ITEM_ERROR = "You cant't have an empty list item"
    class Meta:
        model = Item
        fields = ('text',)
        widgets = {
            'text': forms.fields.TextInput(attrs={
                'placeholder': 'Enter a to-do item',
                'class': 'form-control input-lg',
            }),
        }
        error_messages = {
            'text' : {'required': EMPTY_ITEM_ERROR}
        }
