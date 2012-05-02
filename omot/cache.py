'''
Created on May 1, 2012

@author: random
'''


class Cache(object):
    """
    Simple Python dictionary based object cache 
    """
    cache = {}
    
    @property
    def empty(self):
        """
        Is the cache empty? 
        """
        return len(self.cache) == 0
    
    @property
    def size(self):
        """
        Number of items in cache
        """
        return len(self.cache)
    
    def has(self, key):
        return self.cache.has_key(key)
    
    def put(self, key, value):
        self.cache[key] = value
        
    def get(self, key):
        if not self.cache.has_key(key): 
            return None
        return self.cache[key]
    
    def clear(self):
        self.cache.clear()
        
    def print_keys(self):
        print "Cache [%s]: {" % str(len(self.cache))
        for key in self.cache:
            print "    %s" % key
        print "}"
