from django.urls import re_path

from core.third_party.views.rosetta import (
    rosetta_download_file,
    rosetta_file_list,
    rosetta_form,
    rosetta_redirect,
    rosetta_translate_text,
)

urlpatterns = [
    re_path(
        r"^$",
        rosetta_redirect,
        name="rosetta-old-home-redirect",
    ),
    re_path(
        r"^files/$",
        rosetta_redirect,
        name="rosetta-file-list-redirect",
    ),
    re_path(
        r"^files/(?P<po_filter>[\w-]+)/$",
        rosetta_file_list,
        name="rosetta-file-list",
    ),
    re_path(
        r"^files/(?P<po_filter>[\w-]+)/(?P<lang_id>[\w\-_\.@]+)/(?P<idx>\d+)/$",
        rosetta_form,
        name="rosetta-form",
    ),
    re_path(
        r"^files/(?P<po_filter>[\w-]+)/(?P<lang_id>[\w\-_\.@]+)/(?P<idx>\d+)/download/$",
        rosetta_download_file,
        name="rosetta-download-file",
    ),
    re_path(r"^translate/$", rosetta_translate_text, name="rosetta.translate_text"),
]
