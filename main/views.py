from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .utils.queryGoogleForDirections import getPath
from .utils.apiai import *

def index(request):
    request.session['_messages'] = request.session.get('_messages',
        "Conversations will be displayed below:\n")
    if request.method == "GET":
        return render(request, 'index.html',
            {'messages': request.session['_messages']})
    else:
        #request.session['_messages'] += getPath() +"\n"
        query = request.POST.get('query')
        request.session['_messages'] += query + '\n'
        response = apiai_request(query)
        address1, address2 = get_addresses_from_response(response)
        if not address2:
            request.session['_messages'] += response["result"]["fulfillment"] \
                                                    ["speech"] + '\n'
        else:
            address1 = validate(address1)
            request.session['_messages'] += getPath(address1, address2) + '\n'
        return HttpResponseRedirect(reverse('index'))
