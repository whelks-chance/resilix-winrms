#!/usr/bin/env python
# -*- coding: utf-8 -*-
from resilix import settings

__author__ = 'ian'


from winrm import Protocol
import base64


def get_connection():
    # address = "localhost"
    # transport = "plaintext"
    # username = "admin"
    # password = "admin_password"
    # protocol = "http"
    # port = 5985
    # endpoint = "%s://%s:%s/wsman" % (protocol, address, port)

    address = settings.address
    transport = settings.transport
    username = settings.username
    password = settings.password
    protocol = settings.protocol
    port = settings.port
    endpoint = settings.endpoint

    conn = Protocol(endpoint=endpoint, transport=transport,
                    username=username, password=password)
    shell_id = conn.open_shell()

    return conn, shell_id


def start_service(conn, shell_id, service_name):

    script = 'Start-Service ' + service_name

    # base64 encode, utf16 little endian. required for windows
    encoded_script = base64.b64encode(script.encode("utf_16_le"))

    # send the script to powershell, tell it the script is encoded
    command_id = conn.run_command(shell_id, "powershell -encodedcommand %s" % (encoded_script))
    stdout, stderr, return_code = conn.get_command_output(shell_id, command_id)
    conn.cleanup_command(shell_id, command_id)
    print "STDOUT: %s" % (stdout)
    print "STDERR: %s" % (stderr)


def write_file(conn, shell_id):
    # the text file we want to send
    # this could be populated by reading a file from disk instead
    # has some special characters, just to prove they won't be a problem

    text_file = """this is a multiline file
    that contains special characters such as
    "blah"
    '#@$*&&($}
    that will be written
    onto the windows box"""

    # first part of the powershell script
    # streamwriter is the fastest and most efficient way to write a file
    # I have found
    # notice the @", this is like a "here document" in linux
    # or like triple quotes in python and allows for multiline files
    # the file will be placed in the home dir of the user that
    # logs into winrm (administrator in this case)
    part_1 = """$stream = [System.IO.StreamWriter] "test.txt"
    $s = @"
    """

    # second part of the powershell script
    # the "@ closes the string
    # the replace will change the linux line feed to the
    # windows carriage return, line feed
    part_2 = """
    "@ | %{ $_.Replace("`n","`r`n") }
    $stream.WriteLine($s)
    $stream.close()"""

    # join the beginning of the powershell script with the
    # text file and end of the ps script
    script = part_1 + text_file + part_2

    # base64 encode, utf16 little endian. required for windows
    encoded_script = base64.b64encode(script.encode("utf_16_le"))

    # send the script to powershell, tell it the script is encoded
    command_id = conn.run_command(shell_id, "powershell -encodedcommand %s" % (encoded_script))
    stdout, stderr, return_code = conn.get_command_output(shell_id, command_id)
    conn.cleanup_command(shell_id, command_id)
    print "STDOUT: %s" % (stdout)
    print "STDERR: %s" % (stderr)


def write_out_file(conn, shell_id):
    # print the file
    command_id = conn.run_command(shell_id, "type test.txt")
    stdout, stderr, return_code = conn.get_command_output(shell_id, command_id)
    conn.cleanup_command(shell_id, command_id)
    print "STDOUT: %s" % (stdout)
    print "STDERR: %s" % (stderr)


def delete_file(conn, shell_id):
    # delete the file
    command_id = conn.run_command(shell_id, "del test.txt")
    stdout, stderr, return_code = conn.get_command_output(shell_id, command_id)
    conn.cleanup_command(shell_id, command_id)
    print "STDOUT: %s" % (stdout)
    print "STDERR: %s" % (stderr)


def do_stuff():
    conn, shell_id = get_connection()
    write_file(conn, shell_id)
    write_out_file(conn, shell_id)
    delete_file(conn, shell_id)


def list_service_data(conn, shell_id, service_name):

    script = """$service = Get-WmiObject -ComputerName $env:computername -Class Win32_Service `
-Filter "Name='""" + service_name + """'"
$service
$service | Get-Member -Type Method
$pid_for_service = $service | select -expand ProcessId
$pid_for_service
(Get-Process -id $pid_for_service).StartInfo | select -ExpandProperty environmentvariables
"""
    stdout, stderr = run_script(conn, shell_id, script)

    return stdout, stderr, script


def list_pcs(conn, shell_id, service_name):

    scripts = [
        """get-service""",
        """$PSVersionTable.PSVersion""",
        """Get-ADComputer -Filter * -Property * |
        Format-Table Name,OperatingSystem,OperatingSystemServicePack,OperatingSystemVersion -Wrap -Auto""",
        """Test-WsMan DC01""",
        """Test-WsMan EX01""",
        """$password = ConvertTo-SecureString "Viavmops1" -AsPlainText -Force
        $cred= New-Object System.Management.Automation.PSCredential ("AD\Administrator", $password )
        $session = New-PSSession -ComputerName EX01 -Credential $cred
        Invoke-Command -Session $session -ScriptBlock { hostname }"""

    ]

    outputs = []
    stdout = ''
    stderr = ''
    for script in scripts:
        stdout1, stderr1 = run_script(conn, shell_id, script)
        outputs.append({
            'stdout': stdout1,
            'stderr': stderr1
        })

        stdout += stdout1 + '\n\n'

        if len(stderr1.strip()):
            stderr += script + stderr1 + '\n\n'

    return stdout, stderr, '\n'.join(scripts)


def run_script(conn, shell_id, script):
    # base64 encode, utf16 little endian. required for windows
    encoded_script = base64.b64encode(script.encode("utf_16_le"))

    # send the script to powershell, tell it the script is encoded
    command_id = conn.run_command(shell_id, "powershell -encodedcommand %s" % (encoded_script))
    stdout, stderr, return_code = conn.get_command_output(shell_id, command_id)
    conn.cleanup_command(shell_id, command_id)
    print "STDOUT: %s" % (stdout)
    print "STDERR: %s" % (stderr)

    return stdout, stderr

    # conn1, shell_id1 = get_connection()
    # # do_stuff()
    # start_service(conn1, shell_id1, 'SkypeUpdate')
    # list_service_data(conn1, shell_id1, 'SkypeUpdate')