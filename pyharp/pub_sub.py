class Observer(object):
    def notify(self, *args, **kwargs):
        raise NotImplementedError

class Target(object):

    def __init__(self, *observers):
        self.observes = list(observers)

    def observe(self, observer):
        if observer in self.observes:
            return
        self.observes += [observer]

    # this notify for every access to the function
    def emit(self, topic, *args, **kwargs):
        for obs in self.observes:
            obs.notify(topic, *args, **kwargs)
