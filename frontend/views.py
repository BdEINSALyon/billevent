from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView


class VueAppView(TemplateView):
    template_name = 'index.html'
