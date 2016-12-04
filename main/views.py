from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .utils.queryGoogleForDirections import getPath

def index(request):
    request.session['_messages'] = request.session.get('_messages',
        "Conversations will be displayed below:\n")
    if request.method == "GET":
        return render(request, 'index.html',
            {'messages': request.session['_messages']})
    else:
        request.session['_messages'] += getPath() +"\n"
        #request.POST.get('query')
        return HttpResponseRedirect(reverse('index'))
