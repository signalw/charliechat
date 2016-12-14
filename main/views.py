# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser, User
from django.utils import timezone
from .utils.dialog import *
from .utils.recommend import recommend_meal
from .models import Profile, Query

FIRST_TIME_MSG = "Welcome to CharlieChat! Are you new to the area?"

def index(request):
    request.session['_messages'] = request.session.get('_messages',
        [msg('charliechat',FIRST_TIME_MSG)]) # first time ever using
    request.session['_historyQueries'] = request.session.get('_historyQueries',[]) # previous query responses
    request.session['_historyIntents'] = request.session.get('_historyIntents',[])
    request.session['_historyDestinations'] = request.session.get('_historyDestinations',[]) # previous places user wanted to go
    request.session['_historyYelp'] = request.session.get('_historyYelp',[])
    request.session['_unfinished'] = request.session.get('_unfinished',{}) # queries that need more info to finish
    request.session['_suggestedMeal'] = request.session.get('_suggestedMeal',False)

    # display the page
    if request.method == "GET":       
        return render(request, 'index.html',
            {'messages': request.session['_messages']})
    # clear messages
    elif request.method == "POST" and request.POST.get('clear_messages'):
        request.session['_messages'] =  [cc_msg("That's all gone!"),cc_msg(FIRST_TIME_MSG)]
        request.session['_historyQueries'] = []
        request.session['_historyIntents'] = []
        request.session['_historyDestinations'] = []
        request.session['_historyYelp'] = []
        request.session['_unfinished'] = {}
        request.session['_suggestedMeal'] = False
        return HttpResponseRedirect(reverse('index'))
    # dialog time
    else:
        query = request.POST.get('query')
        geo_loc = request.POST.get('geo_loc')
        request.session['_messages'].append({'author':'user','msg':query})

        q = Query()
        if not isinstance(request.user, AnonymousUser):
            q.user = request.user
        else:
            q.user = User.objects.get(username="admin")
        q.raw_query = query
        q.add_date = timezone.now()
        q.save()
        dialog_flow(request,query,geo_loc)
        recommend_meal(request,geo_loc)
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
