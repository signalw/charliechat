from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .utils.queryGoogleForDirectionsv3 import return_travel_info
from .utils.apiai import *

def index(request):
    request.session['_messages'] = request.session.get('_messages',
        "Conversations will be displayed below:\n")
    if request.method == "GET":
        return render(request, 'index.html',
            {'messages': request.session['_messages']})
    elif request.method == "POST" and request.POST.get('clear_messages'):
        request.session['_messages'] = "Conversations will be displayed below:\n"
        return HttpResponseRedirect(reverse('index'))
    else:
        query = request.POST.get('query')
        geo_loc = request.POST.get('geo_loc')

        request.session['_messages'] += query + '\n'
        response = apiai_request(query)
        if get_intent_from_response(response) == "direction":
            # if intent is direction
            address1, address2 = get_addresses_from_response(response)
            if not address2:
                request.session['_messages'] += response["result"] \
                                                ["fulfillment"]["speech"]+'\n'
            else:
                if (validate(address1) is "current_loc"):
                    address1 = geo_loc
                request.session['_messages'] += str(return_travel_info(address1, address2))+'\n'
            return HttpResponseRedirect(reverse('index'))
        else:
            # if intent is not direction
            request.session['_messages'] += response["result"]["fulfillment"] \
                                                    ["speech"]+'\n'
            return HttpResponseRedirect(reverse('index'))
