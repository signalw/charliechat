from django.shortcuts import render
#from django.http import HttpResponse
#from django.template import loader

# Create your views here.

def index(request):
    request.session['_messages'] = request.session.get('_messages', "Conversations will be displayed below:\n")
    if request.method == "GET":
        return render(request, 'index.html', {'messages': request.session['_messages']})
    else:
        request.session['_messages'] += request.POST.get('query')+"\n"
        return render(request, 'index.html', {'messages': request.session['_messages']})
