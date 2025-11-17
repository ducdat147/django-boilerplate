from django.urls import re_path, reverse_lazy
from django.views.generic.base import RedirectView
from rosetta.views import TranslationFileDownload, translate_text

from core.third_party.views.admin import TranslationFileListView, TranslationFormView

urlpatterns = [
    re_path(
        r"^$",
        RedirectView.as_view(
            url=reverse_lazy("rosetta-file-list", kwargs={"po_filter": "project"}),
            permanent=False,
        ),
        name="rosetta-old-home-redirect",
    ),
    re_path(
        r"^files/$",
        RedirectView.as_view(
            url=reverse_lazy("rosetta-file-list", kwargs={"po_filter": "project"}),
            permanent=False,
        ),
        name="rosetta-file-list-redirect",
    ),
    re_path(
        r"^files/(?P<po_filter>[\w-]+)/$",
        TranslationFileListView.as_view(),
        name="rosetta-file-list",
    ),
    re_path(
        r"^files/(?P<po_filter>[\w-]+)/(?P<lang_id>[\w\-_\.@]+)/(?P<idx>\d+)/$",
        TranslationFormView.as_view(),
        name="rosetta-form",
    ),
    re_path(
        r"^files/(?P<po_filter>[\w-]+)/(?P<lang_id>[\w\-_\.@]+)/(?P<idx>\d+)/download/$",
        TranslationFileDownload.as_view(),
        name="rosetta-download-file",
    ),
    re_path(r"^translate/$", translate_text, name="rosetta-translate_text"),
]
