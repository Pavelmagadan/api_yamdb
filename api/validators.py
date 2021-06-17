
from django.core.exceptions import ValidationError
from datetime import datetime


def year_validator(value):
    if value > datetime.now().year:
        raise ValidationError(
            ('%(value)s is not a correcrt year!'),
            params={'value': value},
        )
