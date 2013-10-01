import threading
from time_helper import get_time
from traceback import print_exc

class Job(object):
    TOTALS = 0
    UNFINISHED_COUNT = 0
    id = None

    def __init__(self, callableObj, *args, **kwargs):
        self.action = callableObj
        self.args = args
        self.kwargs = kwargs
        # counts and such
        Job.TOTALS = Job.TOTALS + 1
        self.id = Job.TOTALS
        Job.UNFINISHED_COUNT = Job.UNFINISHED_COUNT + 1

    def execute(self):
        print "\t Job #%s STARTED @ %s -- Remaining: %s." % (self.id, get_time(), Job.UNFINISHED_COUNT)
#         print "\t action: %r (%r, %r)" % (self.action, self.args, self.kwargs)
        try:
            self.action(*self.args, **self.kwargs)
        except Exception, e:
            print_exc(e)
        Job.UNFINISHED_COUNT = Job.UNFINISHED_COUNT - 1
        print "\t Job #%s FINISHED @ %s -- Remaining: %s" % (self.id, get_time(), Job.UNFINISHED_COUNT)

class ThreadJobs(threading.Thread):
    """Threaded Url Grab"""

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # grabs host from queue
            job = self.queue.get()

            try:
                job.execute()
            except:
                pass

            # signals to queue job is done
            self.queue.task_done()