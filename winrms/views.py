from django.shortcuts import render

# Create your views here.
from django.template import RequestContext
from winrms.lib_tests.winrm_test import write_a_file


def index(request):
    return render(request, 'home.html', {'data': 'hello world'}, context_instance=RequestContext(request))


def do_thing(text):
    print text
    write_a_file(text)


def write_file(request):
    do_thing(request.GET.get('to_write', 'failed'))
    return index(request)