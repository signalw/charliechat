# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from .utils.dialog import *

FIRST_TIME_MSG = "Welcome to CharlieChat! Are you new to the area?"

def index(request):
    request.session['_messages'] = request.session.get('_messages',
        [msg('charliechat',FIRST_TIME_MSG)]) # first time ever using
    request.session['_historyQueries'] = request.session.get('_historyQueries',[]) # previous query responses
    request.session['_historyIntents'] = request.session.get('_historyIntents',[])
    request.session['_historyDestinations'] = request.session.get('_historyDestinations',[]) # previous places user wanted to go
    request.session['_unfinished'] = request.session.get('_unfinished',{}) # queries that need more info to finish

    # display the page
    if request.method == "GET":
        return render(request, 'index.html',
            {'messages': request.session['_messages']})
    # clear messages
    elif request.method == "POST" and request.POST.get('clear_messages'):
        request.session['_messages'] =  [msg('charliechat',"That's all gone!")]
        request.session['_historyQueries'] = []
        request.session['_historyIntents'] = []
        request.session['_historyDestinations'] = []
        request.session['_unfinished'] = {}
        return HttpResponseRedirect(reverse('index'))
    # dialog time
    else:
        query = request.POST.get('query')
        geo_loc = request.POST.get('geo_loc')

        request.session['_messages'].append({'author':'user','msg':query})

        dialog_flow(request,query,geo_loc)
        return HttpResponseRedirect(reverse('index'))

def about(request):
    if request.method == "GET":
        return render(request, 'about.html')

@login_required
def settings(request):
    if request.method == "GET":
        return render(request, 'settings.html',
            {'groups': ["-- select an option --","tourist","worker","student"]})
    else:
        u = request.user
        u.profile.group = request.POST.get('group')
        u.profile.bio = request.POST.get('bio')
        u.save()
        return HttpResponseRedirect(reverse('settings'))
