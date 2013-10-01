
import urllib2
import base64

def base64_encode(filename = None, url = None):
    """
    Given a filename or url, converts the content into base64 string.
    
    :param filename: absolute or relative path to file.
    :param url: a well-formated url.
    
    :returns: A base64 string
    """
    if url:
        content = urllib2.urlopen(url).read()
    elif filename:
        content = get_file_content(filename)
    else:
        content = ''
    return base64.b64encode(content)