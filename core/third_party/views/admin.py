from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from markupsafe import Markup
from rosetta.views import TranslationFileListView as BaseTranslationFileListView
from rosetta.views import TranslationFormView as BaseTranslationFormView

from core.sites import each_context


class TranslationFileListView(BaseTranslationFileListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Translation File List")
        context["data_languages"] = [
            {
                "title": language,
                "data": {
                    "headers": [
                        _("Application"),
                        _("Progress"),
                        _("Messages"),
                        _("Translated"),
                        _("Fuzzy"),
                        _("Obsolete"),
                        _("File"),
                    ],
                    "rows": [
                        [
                            Markup(
                                '<a href="%s">%s</a>'
                                % (
                                    reverse_lazy(
                                        "admin:rosetta-form",
                                        kwargs={
                                            "po_filter": self.po_filter,
                                            "lang_id": lid,
                                            "idx": pos.index((app, path, po)),
                                        },
                                    ),
                                    str(app).replace("_", " ").title(),
                                )
                            ),
                            po.percent_translated(),
                            len(po.translated_entries())
                            + len(po.untranslated_entries()),
                            len(po.translated_entries()),
                            len(po.fuzzy_entries()),
                            len(po.obsolete_entries()),
                            str(path).replace(str(settings.BASE_DIR), "."),
                        ]
                        for app, path, po in pos
                    ],
                },
            }
            for lid, language, pos in context["languages"]
        ]

        context["navigation"] = [
            {
                "title": _("Project"),
                "link": reverse_lazy(
                    "rosetta-file-list", kwargs={"po_filter": "project"}
                ),
                "active": self.po_filter == "project",
            },
            {
                "title": _("Third-Party"),
                "link": reverse_lazy(
                    "rosetta-file-list", kwargs={"po_filter": "third-party"}
                ),
                "active": self.po_filter == "third-party",
            },
            {
                "title": _("Django"),
                "link": reverse_lazy(
                    "rosetta-file-list", kwargs={"po_filter": "django"}
                ),
                "active": self.po_filter == "django",
            },
            {
                "title": _("All"),
                "link": reverse_lazy("rosetta-file-list", kwargs={"po_filter": "all"}),
                "active": self.po_filter == "all",
            },
        ]
        context = {**context, **each_context(self.request)}
        return context


class TranslationFormView(BaseTranslationFormView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = (
            f"{context['rosetta_i18n_lang_name']} - {context['rosetta_i18n_pofile'].percent_translated()}%"
        )
        context["navigation"] = [
            {
                "title": _("All"),
                "link": f"?{context['filter_query_string_base']}&msg_filter=all",
                "active": self.msg_filter == "all",
            },
            {
                "title": _("Untranslated only"),
                "link": f"?{context['filter_query_string_base']}&msg_filter=untranslated",
                "active": self.msg_filter == "untranslated",
            },
            {
                "title": _("Translated only"),
                "link": f"?{context['filter_query_string_base']}&msg_filter=translated",
                "active": self.msg_filter == "translated",
            },
            {
                "title": _("Fuzzy only"),
                "link": f"?{context['filter_query_string_base']}&msg_filter=fuzzy",
                "active": self.msg_filter == "fuzzy",
            },
        ]
        context = {**context, **each_context(self.request)}
        context["scripts"] += [static("admin/rosetta/js/rosetta.js")]
        return context
