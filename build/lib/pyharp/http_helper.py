from datetime import datetime
from time import time, sleep
import os
from urlparse import urlsplit, urlparse
import requests
import shutil
from os.path import basename
from file_system import get_file_content, format_filesize
from file_naming import safe_filename
from time_helper import get_time
from queue_system import Job
from pub_sub import Target
import json

DESKTOP_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0'

def url2name(url):
    return basename(urlsplit(url)[2])

def cookie_to_cookies(cookie):
    cookies = {}
    if not isinstance(cookie, type('')):
        return cookie or cookies
    for cookie_item in cookie.split(';'):
        key, _, value, = cookie_item.partition('=')
        cookies[key] = value
    return cookies


#===============================================================================
# Download Log
#===============================================================================
def was_downloaded(download_logs, filename):
    file_content = get_file_content(download_logs)
    # print file_content
    if filename in file_content:
        return True
    return False

def update_log(download_logs, filename):
    if not download_logs:
        return

    if was_downloaded(download_logs, filename):
        print "Already in list: %s" % filename
        return False
    outfile = file(download_logs, 'a')
    outfile.writelines(filename + "\n")
    outfile.close()
    return True


# source: http://stackoverflow.com/questions/862173/how-to-download-a-file-using-python-in-a-smarter-way/863017#863017
def download_file(url,
        base_path = None,
        localFileName = None,
        cookie = None,
        referer = None,
        download_logs = None
        , observer = None):

    def emit(progress):
        if not observer:
            return
        observer.notify('progress:change', progress)

    print "\t\t|- Downloading...: %s" % url
    #===========================================================================
    # create http request
    #===========================================================================
    headers = {
#        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#        'Accept-Encoding': 'gzip, deflate',
#        'Accept-Language': 'en-US,en;q=0.5',
#        'Connection': 'keep-alive',
#        'DNT': '1',
#        'Host': 'media.cdn.pz10.com',
        'Cookie': cookie,
        'Referer': referer or url,
        'User-Agent': DESKTOP_USER_AGENT
    }
    response = requests.get(url, headers = headers, stream = True)
#    print response.text

    #===========================================================================
    # Figure out filename
    #===========================================================================
    if localFileName:
        # we can force to save the file as specified name
        localName = localFileName
    else:
        localName = url2name(url)
        if response.headers.get('Content-Disposition'):
            # If the response has Content-Disposition, we take file name from it
            localName = response.headers['Content-Disposition'].split('filename=')[1]
            if localName[0] == '"' or localName[0] == "'":
                localName = localName[1:-1]
        elif response.url != url:
            # if we were redirected, the real file name we take from the final URL
            localName = url2name(response.url)

    #===========================================================================
    # create full path
    #===========================================================================
    localName = safe_filename(localName)
    # Create the temp folder, if not there
    file_path = '%s/%s' % (base_path, localName)
    temp_path = '../src/temp/' + localName
    if base_path[-1] == '/':
        file_path = '%s%s' % (base_path, localName)

    # Check the file has not been downloaded.
    if download_logs and was_downloaded(download_logs, localName):
        print "\t\t\t   |- Already downloaded: %s" % localName
        emit(100)
        return False

    #===========================================================================
    # download and save the file
    #===========================================================================
    print "\t\t\t|- Save file: %s" % file_path
#    print response.headers
    response_size = int(response.headers.get('content-length', 1))
    if os.path.exists(file_path):
        local_size = os.path.getsize(file_path)
        print "\t\t\t   |- local_size (%s) >= response_size (%s) :: %s" % (local_size, response_size, local_size >= response_size)
        if local_size >= response_size:
            print "\t\t\t|- Already finished: %s" % localName
            update_log(download_logs, localName)
            emit(100)
            return False
    else:
        local_size = -1

    # if response.info().has_key('Content-Length'):
    #    response_size = int( response.info()['Content-Length'] )
    with open(temp_path, 'wb') as file_handle:
        #===========================================================================
        # progressive download
        #===========================================================================
        start_time = time()
        bytes_recieved = 0
        # 1 megabyte = 1 048 576 bytes
        # 100 kilobytes = 102 400 bytes
        chunk_size = 102400
        old_percent = -1
        no_amount_tries = 0
        MAX_RETRIES = 5
        for chunk in response.iter_content(chunk_size = chunk_size):
            file_handle.write(chunk)
            # progress tracking
            bytes_len = len(chunk)
            bytes_recieved += bytes_len
            new_percent = int(float(bytes_recieved) / response_size * 100)
            if new_percent > old_percent:
                emit(new_percent)
                print "\t\t\t\t%s :: %s%%  @ %s" % (localName, new_percent, get_time())

            # we want to detect if we are not getting any data.
            old_percent = new_percent
            if bytes_len == 0:
                no_amount_tries += 1
            else:
                no_amount_tries = 0

    # Conclude
    if no_amount_tries >= MAX_RETRIES or bytes_recieved != response_size:
        print "\n\t\t\t |- FAILURE DUE TO INCOMPLETE :: %s / %s" % (format_filesize(bytes_recieved), format_filesize(response_size))
    else:
        end_time = time()
        update_log(download_logs, localName)
        shutil.move(temp_path, file_path)
        print "\n\t\t\t |- FINISHED %s :: %s / %s in %d seconds." % (localName, format_filesize(bytes_recieved), format_filesize(response_size), end_time - start_time)

def get_hostname(url):
    return urlparse(url).netloc

def get_content(url, cookie = None, referer = None):
    headers = {
#        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#        'Accept-Encoding': 'gzip, deflate',
#        'Accept-Language': 'en-US,en;q=0.5',
#        'Connection': 'keep-alive',
#        'DNT': '1',
#        'Host': get_hostname(url),
        'Cookie': cookie,
        'Referer': referer or url,
        'User-Agent': DESKTOP_USER_AGENT
    }
    response = requests.get(url, headers = headers)
    return response.content

class DownloadJob(Job):

    signals = Target

    def __init__(self, page, observer = None):
        self.signals = Target()
        self.page = page
#         print 'DownloadJob: %r' % page['title']

        super(DownloadJob, self).__init__(download_file
            , page['download']['url']
            , page['download']['base_path']
            , localFileName = page['download']['localFileName']
            , cookie = page['download']['cookie']
            , referer = page['download']['url']
            , download_logs = page['download']['download_logs']
            , observer = self
            )
        page['statusText'] = 'IN_DOWNLOAD_QUEUE'
        if observer:
            self.signals.observe(observer)
#             print 'observes: %r' % self.signals.observes
            self.signals.emit('page:change', object = page)

    def notify(self, topic, value):
#         print 'DownloadJob.notify: %r = %r' % (topic, value)
        if topic == 'progress:change':
            self.page['download']['progress'] = value
            if 0 < value < 100:
                self.page['download']['statusText'] = 'RUNNING'
            elif value == 100:
                self.page['download']['statusText'] = 'FINISHED'
                self.page['finishedOn'] = datetime.utcnow().isoformat() 

            self.signals.emit('page:change', object = self.page)

def create_response(command_title, objects):
    response = {
        'meta': {
            'command': command_title
        },
        'objects': objects
    }
    return json.dumps(response)
