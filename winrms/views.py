from django.shortcuts import render

# Create your views here.
from django.template import RequestContext
from winrms.lib_tests.winrm_test import *


def index(request):
    return render(request, 'home.html', {'data': 'hello world'}, context_instance=RequestContext(request))


def do_thing(text):
    print text
    conn, shell_id = get_connection()
    stdout, stderr, script = list_service_data(conn, shell_id, text)
    return stdout, stderr, script

def service_info(request):
    service_name = request.GET.get('service_name', 'MISSING_FIELD')
    stdout, stderr, script = do_thing(service_name)
    return render(request, 'home.html', {
        'service_name': service_name,
        'stdout': stdout,
        'stderr': stderr,
        'script': script
    }, context_instance=RequestContext(request))
