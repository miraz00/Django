import random

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django import forms
from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def show_page(request, name):
    if not util.get_entry(name):
        return render(request, "encyclopedia/page.html", {
            "error": "Page not found!",
            "page_name": "Not Found"
        })
    return render(request, "encyclopedia/page.html", {
        "page": util.md_to_html(util.get_entry(name)),
        "page_name": name
    })


def search_results(request):
    if not request.GET.get("q"):
        return HttpResponse("Empty string submitted")
    else:
        if util.get_entry(request.GET.get("q")):
            return redirect("encyclopedia:show page", name=request.GET.get("q"))
        return render(request, "encyclopedia/search_results.html", {
            "results": [result for result in util.list_entries() if request.GET.get("q").lower() in result.lower()]
        })


class CreatePageForm(forms.Form):
    title = forms.CharField(label="Title", required=True)
    content = forms.CharField(widget=forms.Textarea, label="Content", required=True)


def create_page(request):
    if request.method == "POST":
        form = CreatePageForm(request.POST)
        if form.is_valid():
            if util.save_entry(form.cleaned_data["title"], form.cleaned_data["content"]) == 3:
                return render(request, "encyclopedia/create_page.html", {
                    "form": form,
                    "error": "The entry already exists for this title!"
                })
            return render(request, "encyclopedia/page.html", {
              "page": util.md_to_html(util.get_entry(form.cleaned_data["title"])),
              "page_name": form.cleaned_data["title"],
              "success_msg": "New page has been added successfully!"
            })

        else:
            return render(request, "encyclopedia/create_page.html", {
                "form": form,
                "error": "Please fill both fields!"
            })

    return render(request, "encyclopedia/create_page.html", {
        "form": CreatePageForm()
    })


class EditPageForm(CreatePageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['readonly'] = 'readonly'


def edit_page(request, name):
    if request.method == "GET":
        request.session["title"] = name
        initial_data = {
            "title": name,
            "content": util.get_entry(name)
        }
        return render(request, "encyclopedia/create_page.html", {
            "form": EditPageForm(initial=initial_data),
            "edit": name
        })

    form = EditPageForm(request.POST)
    if form.is_valid() and request.session["title"] == form.cleaned_data["title"]:
        del request.session["title"]
        util.save_entry(form.cleaned_data["title"], form.cleaned_data["content"], True)
        return render(request, "encyclopedia/page.html", {
            "page": util.md_to_html(util.get_entry(request.POST.get("title"))),
            "page_name": request.POST.get("title"),
            "success_msg": "Successfully updated the page"
        })
    elif request.session["title"] != form.cleaned_data["title"]:
        return render(request, "encyclopedia/create_page.html", {
            "form": EditPageForm(initial={'title': request.session["title"], 'content': form.cleaned_data["content"]}),
            "edit": request.session["title"],
            "error": "You can't change the title!"
        })
    else:
        return render(request, "encyclopedia/create_page.html", {
            "form": form,
            "edit": form.cleaned_data["title"],
            "error": "Content field cannot be empty!"
        })


def random_page(request):
    return show_page(request, (random.choice(util.list_entries())))
