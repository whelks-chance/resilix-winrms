from django.shortcuts import render

# Create your views here.
from django.template import RequestContext
import re
from winrms.lib_tests.winrm_test import *


def index(request):
    return render(request, 'home.html', {'data': 'hello world'}, context_instance=RequestContext(request))


def do_thing(text, task):
    print text
    conn, shell_id = get_connection()

    if task == 'list_service':
        stdout, stderr, script = list_service_data(conn, shell_id, text)
    elif task == 'find_pcs':
        stdout, stderr, script = list_pcs(conn, shell_id, text)
    else:
        stdout, stderr, script = ('', '', '')

    return stdout, stderr, script


def service_info(request):
    service_name = request.GET.get('service_name', 'MISSING_FIELD')
    stdout, stderr, script = do_thing(service_name, 'list_service')
    return render(request, 'home.html', {
        'service_name': service_name,
        'stdout': stdout,
        'stderr': stderr,
        'script': script
    }, context_instance=RequestContext(request))


def find_pcs(request):
    service_name = request.GET.get('service_name', 'MISSING_FIELD')
    stdout, stderr, script = do_thing(service_name, 'find_pcs')
    # stderr = format_output(stderr)
    return render(request, 'home.html', {
        'service_name': service_name,
        'stdout': stdout,
        'stderr': stderr,
        'script': script
    }, context_instance=RequestContext(request))


def format_output(input):
    stderr_arr = input.split('>')
    formatted_stderr = ''
    indent = 0
    for tag in stderr_arr:

        if '</' in tag:

            for i in range(0, indent):
                formatted_stderr += '....'

            close_tag_arr = tag.split('</')
            formatted_stderr += close_tag_arr[0] + '\n'

            indent -= 1

            for i in range(0, indent):
                formatted_stderr += '....'
            formatted_stderr += '</' + close_tag_arr[1] + '>\n'

        else:
            if '/>' in tag:
                indent -= 1

            else:
                for i in range(0, indent):
                    formatted_stderr += '....'

                indent += 1
                formatted_stderr += tag + '>\n'
    return formatted_stderr