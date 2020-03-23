from django.shortcuts import render
from django.views.generic.edit import FormView
from django.views.generic import ListView, TemplateView
from django.urls import reverse_lazy

from .models import ProjFinder
from .forms import ProjFinderForm

class ProjFinderView(TemplateView):
    template_name = 'projfinder.html'
    #success_url = reverse_lazy('routes')

    proj_finder = ProjFinder()
    routes = proj_finder.main()
    extra_context = {}
    extra_context['route'] = routes

def proj_finder_view(request):
    context = {}
    proj_finder = ProjFinder()

    if request.method == 'POST':
        form = ProjFinderForm(request.POST)
        context['form'] = form
        if form.is_valid():
            #update routes
            #location = get_location()
            #routes = ProjFinder(location = location, min_grade = form.min_grade, max_distance = form.max_distance) 
            routes = proj_finder.main(min_grade = form.cleaned_data.get('min_grade'))
            context['routes'] = routes
            return render(request, 'projfinder.html', context)
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
                return render(request, 'projfinder.html', context)

    form = ProjFinderForm()
    routes = proj_finder.main()
    context['form'] = form
    context['routes'] = routes
    #context['location'] = proj_finder.llocation

    return render(request, 'projfinder.html', context)
