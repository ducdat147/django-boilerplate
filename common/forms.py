from django import forms
from django.conf import settings

from unfold.widgets import (
    UnfoldAdminCheckboxSelectMultiple,
    UnfoldAdminDateWidget,
    UnfoldAdminDecimalFieldWidget,
    UnfoldAdminEmailInputWidget,
    UnfoldAdminFileFieldWidget,
    UnfoldAdminImageSmallFieldWidget,
    UnfoldAdminIntegerFieldWidget,
    UnfoldAdminRadioSelectWidget,
    UnfoldAdminSelectMultipleWidget,
    UnfoldAdminSelectWidget,
    UnfoldAdminSplitDateTimeWidget,
    UnfoldAdminTextareaWidget,
    UnfoldAdminTextInputWidget,
    UnfoldAdminTimeWidget,
    UnfoldAdminUUIDInputWidget,
)

WIDGET_FOR_FORM = {
    forms.CharField: UnfoldAdminTextInputWidget,
    forms.IntegerField: UnfoldAdminIntegerFieldWidget,
    forms.FloatField: UnfoldAdminDecimalFieldWidget,
    forms.DecimalField: UnfoldAdminDecimalFieldWidget,
    forms.DateField: UnfoldAdminDateWidget,
    forms.TimeField: UnfoldAdminTimeWidget,
    forms.DateTimeField: UnfoldAdminSplitDateTimeWidget,
    forms.BooleanField: UnfoldAdminSelectWidget,
    forms.EmailField: UnfoldAdminEmailInputWidget,
    forms.ChoiceField: UnfoldAdminSelectWidget,
    forms.ModelChoiceField: UnfoldAdminSelectWidget,
    forms.ModelMultipleChoiceField: UnfoldAdminSelectMultipleWidget,
    forms.ImageField: UnfoldAdminImageSmallFieldWidget,
    forms.FileField: UnfoldAdminFileFieldWidget,
    forms.URLField: UnfoldAdminTextInputWidget,
    forms.PasswordInput: UnfoldAdminTextInputWidget,
    forms.Textarea: UnfoldAdminTextareaWidget,
    forms.TypedChoiceField: UnfoldAdminRadioSelectWidget,
    forms.RadioSelect: UnfoldAdminRadioSelectWidget,
    forms.CheckboxSelectMultiple: UnfoldAdminCheckboxSelectMultiple,
    forms.NumberInput: UnfoldAdminIntegerFieldWidget,
    forms.UUIDField: UnfoldAdminUUIDInputWidget,
}


class BaseForm(forms.Form):
    class Media:
        js = getattr(settings, "DEFAULT_FORM_MEDIA_JS", [])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.__class__ = WIDGET_FOR_FORM.get(
                field.__class__,
                UnfoldAdminTextInputWidget,
            )
