from django.test import tag

from users.forms import ReadOnlyLimitedSSNWidget

from .test_setup import TestSetUp


@tag('unit')
class FormsTests(TestSetUp):
    def test_read_only_ssn_widget(self):
        name = "name"
        value = 111111111
        expected = {
            "widget": {
                "name": name,
                "is_hidden": False,
                "required": False,
                "value": str(value),
                "attrs": {},
                "template_name": "auth/widgets/read_only_password_hash.html",
            },
            "summary": [{
                "label": "***-**-"+str(value)[-4:],
            }]
        }
        widget = ReadOnlyLimitedSSNWidget()
        actual = widget.get_context(name, value, {})

        self.assertDictEqual(expected, actual)

    def test_no_ssn_widget(self):
        name = "name"
        value = None
        expected = {
            "widget": {
                "name": name,
                "is_hidden": False,
                "required": False,
                "value": value,
                "attrs": {},
                "template_name": "auth/widgets/read_only_password_hash.html",
            },
            "summary": [{
                "label": "No SSN set.",
            }]
        }
        widget = ReadOnlyLimitedSSNWidget()
        actual = widget.get_context(name, value, {})

        self.assertDictEqual(expected, actual)
