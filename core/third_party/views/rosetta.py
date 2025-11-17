from django.shortcuts import redirect
from django.urls import reverse


def rosetta_redirect(request):
    return redirect("admin:rosetta-file-list", po_filter="project")


def rosetta_file_list(request, **kwargs):
    reverse_url = reverse("admin:rosetta-file-list", kwargs=kwargs)
    params = request.GET.urlencode()
    if not params:
        return redirect(reverse_url)
    return redirect(reverse_url + "?" + params)


def rosetta_form(request, **kwargs):
    reverse_url = reverse("admin:rosetta-form", kwargs=kwargs)
    params = request.GET.urlencode()
    if not params:
        return redirect(reverse_url)
    return redirect(reverse_url + "?" + params)


def rosetta_download_file(request, **kwargs):
    reverse_url = reverse("admin:rosetta-download-file", kwargs=kwargs)
    params = request.GET.urlencode()
    if not params:
        return redirect(reverse_url)
    return redirect(reverse_url + "?" + params)


def rosetta_translate_text(request):
    return redirect("admin:rosetta-translate_text")
