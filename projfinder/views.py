from django.shortcuts import render
from django.views.generic.edit import FormView
from django.views.generic import ListView, TemplateView
from django.urls import reverse_lazy

from .models import ProjFinder
from .forms import ProjFinderForm
from . import defaults

#class ProjFinderView(TemplateView):
#    template_name = 'projfinder.html'
#    #success_url = reverse_lazy('routes')
#
#    projfinder = ProjFinder()
#    routes = projfinder.main()
#    extra_context = {}
#    extra_context['route'] = routes

def projfinder_view(request):
    context      = {}
    projfinder   = ProjFinder()
    form         = ProjFinderForm()
    min_grade    = defaults.MIN_GRADE
    max_grade    = defaults.MAX_GRADE
    max_distance = defaults.MAX_DISTANCE

    if request.method == 'POST':
        form = ProjFinderForm(request.POST)
        if form.is_valid():
            #TODO: Tell User that form was ok
            min_grade    = form.cleaned_data.get('min_grade')
            max_grade    = form.cleaned_data.get('max_grade')
            max_distance = form.cleaned_data.get('max_distance')
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
                return render(request, 'projfinder.html', context)


    context['form'] = form

    routes = projfinder.main(
            request=request,
            min_grade=min_grade,
            max_grade=max_grade,
            max_distance=max_distance,
            )
    context['routes']   = routes
    context['location'] = projfinder.location


    return render(request, 'projfinder.html', context)
