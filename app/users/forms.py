from django.contrib.auth import forms
from django.forms import ModelForm

from users.models import UserRecord


class ReadOnlyLimitedSSNWidget(forms.ReadOnlyPasswordHashWidget):

    def get_context(self, name, value, attrs):
        context = super(forms.ReadOnlyPasswordHashWidget,
                        self).get_context(name, value, attrs)
        summary = []
        if not value:
            summary.append({"label": "No SSN set."})
        else:
            summary.append(
                {"label": f"***-**-{str(value)[-4:]}"})
        context["summary"] = summary
        return context


class ReadOnlyLimitedSSNField(forms.ReadOnlyPasswordHashField):
    widget = ReadOnlyLimitedSSNWidget


class UserRecordForm(ModelForm):

    class Meta:
        model = UserRecord
        fields = ['id', 'email', 'first_name', 'last_name', 'rank',
                  'status', 'ssn',  'user_profile', 'dob', 'branch', 'mos',]


class UserRecordChangeForm(UserRecordForm):
    ssn = ReadOnlyLimitedSSNField(
        label="SSN",
        help_text="Raw passwords are not stored, so there is no way to see "
        "this user’s password, but you can change the password using "
        '<a href="{}">this form</a>.'
    )
