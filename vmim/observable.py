import UserDict

try:
    import uuid as _uuid
    def GenKey():
        return str(_uuid.uuid4())
except ImportError:
    def GenKey():
        from commands import getstatusoutput as run
        s, o = run('uuidgen')
        if s == 0:
            return o
        else:
            raise ImportError("Missing uuid library (and can't fake it)")


class Observable:
    def __init__(self, initialValue=None):
        self.data = initialValue
        self.callbacks = {}

    def addCallback(self, key, func):
        self.callbacks[key] = func

    def delCallback(self, key):
        del self.callback[key]

    def _docallbacks(self):
        for func in self.callbacks:
            self.callbacks[func]()

    def set(self, data):
        self.data = data
        self._docallbacks()

    def get(self):
        return self.data
        
    def update(self, data):
        # conveniance function so no need to check old value.
        if self.data != data:
            self.set(data)

    def unset(self):
        self.data = None
        self._docallbacks()
        
class ObservableDict( UserDict.DictMixin):
    def __init__(self):
        self._dict = {}
        self.callbacks = {}

    def __getitem__(self, item):
        self.callbacks = {}
        if not item in self._dict.keys():
            raise KeyError("Item '%s' does not exist" % item)
        return self._dict[item]
        
    def addCbPost(self, key, func):
        self.callbacks[key] = func
        
    def delCbPost(self, key):
        del self.callback[key]
    
    def _doCbPost(self,key):
        #print "doingcallbacks for" ,self, self.callbacks
        for func in self.callbacks:
            self.callbacks[func](key)

    def __setitem__(self, item, value):
        if item in self:
            del self[item]
        self._dict[item] = value
        self._doCbPost(item)

    def __delitem__(self, item):
        if not item in self._dict:
            raise KeyError("Item '%s' does not exist" % item)
        self._doCbPost(item)

    def keys(self):
        return self._dict.keys()
