import re

from models import AnimeForm, AnimeItem
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import csrf
from django.shortcuts import render_to_response

# TODO: Pager here
def index(request):
    return render_to_response('anime/list.html', {
            'list':AnimeItem.objects.all()
            }, context_instance = RequestContext(request))

def info(request, anime_slug=''):
    return render_to_response('anime/view.html', {
            'list':AnimeItem.objects.get(slug=anime_slug)
            }, context_instance = RequestContext(request))

def add(request):
    form = AnimeForm()
    if request.method == 'POST': 
        form = AnimeForm(request.POST, request.FILES) 
        if form.is_valid(): 
            form.save(commit=False)
            slugt = re.sub(r'[^a-z0-9\s-]', ' ', form.title)
            slugt = re.sub(r'\s+', ' ', slugt)
            form.slug = re.sub(r'\s', '-', slugt)
            form.save()
            return HttpResponseRedirect('/thanks/')
        
    ctx = {'form': form}
    ctx.update(csrf(request))
    return render_to_response(
        'anime/add.html', 
        ctx, context_instance = RequestContext(request))
    
