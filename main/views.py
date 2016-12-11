# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .utils.dialog import *

FIRST_TIME_MSG = "Welcome to CharlieChat! Are you new to the area?"

def index(request):
    request.session['_messages'] = request.session.get('_messages',
        [{'author':'charliechat','msg':FIRST_TIME_MSG}]) # first time ever using
    # display the page
    if request.method == "GET":
        return render(request, 'index.html',
            {'messages': request.session['_messages']})
    # clear messages
    elif request.method == "POST" and request.POST.get('clear_messages'):
        request.session['_messages'] =  [{'author':'charliechat','msg':"All gone!"}]
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