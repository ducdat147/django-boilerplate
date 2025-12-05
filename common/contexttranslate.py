from django.utils.translation import gettext_lazy as _

CONTEXT = (
    _("Search apps and models..."),
    _("No results found"),
    _("This page yielded into no results. Create a new item or reset your filters."),
    _("Reset filters"),
    _("Hide counts"),
    _("Show counts"),
    _('Choose %s by selecting them and then select the "Choose" arrow button.'),
    _('Remove %s by selecting them and then select the "Remove" arrow button.'),
    _("Raw passwords are not stored, so there is no way to see the user’s password."),
    _(
        "Raw passwords are not stored, so there is no way to see this "
        "user’s password, but you can change the password using "
        '<a href="{}" class="text-primary-600 dark:text-primary-500">this form</a>.'
    ),
)
