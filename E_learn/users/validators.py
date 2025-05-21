import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    def validate(self, password, user=None):
        pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not re.fullmatch(pattern, password):
            raise ValidationError(
                _("Password must be at least 8 characters long and include a letter, a number, and a special character (@$!%*?&)."),
                code='password_invalid',
            )

    def get_help_text(self):
        return _("Your password must include at least one letter, one number, one special character, and be 8+ characters.")
