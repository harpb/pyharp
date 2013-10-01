import re
from django.utils.encoding import smart_str

def get_extension(path_or_url):
    sequence_extract = re.search("\.([0-9a-z]+)$", path_or_url)
    return sequence_extract.group(1)

def safe_filename(filename):
    if not filename:
        return ''
    # filename = re.sub("([^a-zA-Z0-9\.\-\_\s\]\[+)", '_', filename)
    try:
        filename = re.sub('([\\\/\:\;\*\<\>\|\?\"\n\t\r]+)', '_', filename)
        filename = smart_str(filename)
    except TypeError, e:
        print "!!! ERROR -- filename: %s, Exception: %s" % (filename, e)
    MAX_FILENAME_LENGTH = 255
    THRESHOLD = 5
    if len(filename) > MAX_FILENAME_LENGTH + THRESHOLD:
        extension = get_extension(filename)
        filename = filename[:MAX_FILENAME_LENGTH] + '.' + extension
    return filename
