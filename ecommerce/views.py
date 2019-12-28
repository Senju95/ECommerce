from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, get_user_model

from .forms import ContactForm

def home_page(request):
    context = {
        "title" : "My firts Django app!!",
    }
    if request.user.is_authenticated():
        context["premium_content"] = "YEAAA!!!"
    return render(request, "home_page.html", context)

def about_page(request):
    context = {
        "title" : "About page!!"
    }
    return render(request, "home_page.html", context)

def contact_page(request):
    contact_form = ContactForm(request.POST or None)
    context = {
        "title" : "Contact!!",
        "form" : contact_form
    }

    if contact_form.is_valid():
        if request.is_ajax():
            return JsonResponse({"message": "Thank you"})

    if contact_form.errors:
        errors = contact_form.errors.as_json()
        if request.is_ajax():
            return HttpResponse(errors, status=400, content_type='application/json')

    return render(request, "contact/view.html", context)