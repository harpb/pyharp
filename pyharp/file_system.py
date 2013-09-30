import os

#===============================================================================
# Reading file
#===============================================================================
def get_file_content(filename):
    file_handle = file(filename)
    content = []
    for line in file_handle:
        content.append(line.strip())
    file_handle.close()
    return content

def get_dir_content(dirname):
    files = []
    for filename in os.listdir(dirname):
        files.append(filename)
    return files


# soruce : http://code.activestate.com/recipes/82465-a-friendly-mkdir/
def mkdir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            mkdir(head)
        # print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)

def format_filesize(bytes):
    """
    Formats the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB,
    102 bytes, etc).
    """
    try:
        bytes = float(bytes)
    except:
        bytes = -1

    filesize_number_format = lambda value: '%.2f' % value

    if bytes < 1024:
        return "%(size)d bytes" % {'size': bytes}
    if bytes < 1024 * 1024:
        return "%s KB" % filesize_number_format(bytes / 1024)
    if bytes < 1024 * 1024 * 1024:
        return "%s MB" % filesize_number_format(bytes / (1024 * 1024))
    if bytes < 1024 * 1024 * 1024 * 1024:
        return "%s GB" % filesize_number_format(bytes / (1024 * 1024 * 1024))
    if bytes < 1024 * 1024 * 1024 * 1024 * 1024:
        return "%s TB" % filesize_number_format(bytes / (1024 * 1024 * 1024 * 1024))
    return "%s PB" % filesize_number_format(bytes / (1024 * 1024 * 1024 * 1024 * 1024))
