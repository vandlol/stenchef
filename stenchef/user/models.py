from django.db import models
import django.contrib.auth.models as dmodels
from django_currentuser.middleware import get_current_authenticated_user
import uuid
from django.core.validators import RegexValidator
from .fields import IntegerRangeField


class Setting(models.Model):
    settingid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        dmodels.User,
        on_delete=models.CASCADE,
        default=get_current_authenticated_user,
        editable=False,
    )
    bl_consumer_key = models.CharField(
        max_length=35,
        validators=[
            RegexValidator(
                "^[A-Z0-9]*$", "Only uppercase letters and underscores allowed."
            )
        ],
    )
    bl_consumer_secret = models.CharField(
        max_length=35,
        validators=[
            RegexValidator(
                "^[A-Z0-9]*$", "Only uppercase letters and underscores allowed."
            )
        ],
    )
    bl_token_value = models.CharField(
        max_length=35,
        validators=[
            RegexValidator(
                "^[A-Z0-9]*$", "Only uppercase letters and underscores allowed."
            )
        ],
    )
    bl_token_secret = models.CharField(
        max_length=35,
        validators=[
            RegexValidator(
                "^[A-Z0-9]*$", "Only uppercase letters and underscores allowed."
            )
        ],
    )
    percentage_used = IntegerRangeField(
        min_value=-100,
        max_value=100000,
        default=0,
        help_text="Percentage you want to undercut or extend the Mean Price for USED Pieces. Use negative value for undercut.",
    )
    percentage_new = IntegerRangeField(
        min_value=-100,
        max_value=100000,
        default=0,
        help_text="Percentage you want to undercut or extend the Mean Price for NEW Pieces. Use negative value for undercut.",
    )

    def __str__(self):
        return self.owner.username  # pylint: disable=no-member
