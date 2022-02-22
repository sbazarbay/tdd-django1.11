from django import forms
from django.contrib.auth import get_user_model

from lists.models import Item, List

EMPTY_ITEM_ERROR = "You can't have an empty list item"
DUPLICATE_ITEM_ERROR = "You've already got this in your list"
USER_NOT_FOUND_ERROR = "Given email is invalid or doesn't exist"

User = get_user_model()


class ItemForm(forms.models.ModelForm):
    class Meta:
        model = Item
        fields = ("text",)
        widgets = {
            "text": forms.widgets.TextInput(
                attrs={
                    "placeholder": "Enter a to-do item",
                    "class": "form-control input-lg",
                }
            )
        }
        error_messages = {"text": {"required": EMPTY_ITEM_ERROR}}


class NewListForm(ItemForm):
    def save(self, owner):
        if owner.is_authenticated:
            return List.create_new(
                first_item_text=self.cleaned_data["text"], owner=owner
            )
        else:
            return List.create_new(first_item_text=self.cleaned_data["text"])


class ExistingListItemForm(ItemForm):
    def __init__(self, for_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.list = for_list

    def validate_unique(self) -> None:
        try:
            self.instance.validate_unique()
        except forms.ValidationError as e:
            e.error_dict = {"text": [DUPLICATE_ITEM_ERROR]}
            self._update_errors(e)


class ShareListForm(forms.models.ModelForm):
    class Meta:
        model = List
        fields = ("shared_with",)

    def __init__(self, for_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = for_list

    shared_with = forms.EmailField(
        widget=forms.widgets.EmailInput(
            attrs={
                "placeholder": "your-friend@example.com",
            }
        ),
        error_messages={
            "required": USER_NOT_FOUND_ERROR,
            "invalid": USER_NOT_FOUND_ERROR,
        },
    )

    def save(self):
        shared_with = self.cleaned_data["shared_with"]
        user = User.objects.get(pk=shared_with)
        self.instance.shared_with.add(user)

        return self.instance
