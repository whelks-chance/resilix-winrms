__author__ = 'ian'

# Some variables for winrms connections

address = "localhost"
transport = "plaintext"
username = "winrms"
password = "resilix4me"
protocol = "http"
port = 5985

endpoint = "%s://%s:%s/wsman" % (protocol, address, port)
