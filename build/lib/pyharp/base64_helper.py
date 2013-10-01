
import urllib2
import base64

def base64_encode(filename = None, url = None):
    if url:
        content = urllib2.urlopen(url).read()
    return base64.b64encode(content)