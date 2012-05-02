'''
Created on May 1, 2012

@author: random
'''
import os
import sys


def find_path(filename):
    full_filename = None
    if os.path.exists(os.path.join(os.path.split(__file__)[0], filename)):
        full_filename = os.path.join(os.path.split(__file__)[0], filename)
    elif os.path.exists(os.path.join(os.path.split(__file__)[0], 'pixmaps', filename)):
        full_filename = os.path.join(os.path.split(__file__)[0], 'pixmaps', filename)
    elif os.path.exists(os.path.join(os.path.split(__file__)[0], 'share', filename)):
        full_filename = os.path.join(os.path.split(__file__)[0], 'share', filename)
    elif os.path.exists(os.path.join(__file__.split('/lib')[0], 'share', 'pixmaps', filename)):
        full_filename = os.path.join(__file__.split('/lib')[0], 'share', 'pixmaps', filename)
    elif os.path.exists(os.path.join(sys.prefix, 'share', 'pixmaps', filename)):
        full_filename = os.path.join(sys.prefix, 'share', 'pixmaps', filename)
    assert full_filename
    return full_filename


def memory_usage():
    """Memory usage of the current process in kilobytes."""
    status = None
    result = {'peak': 0, 'rss': 0}
    try:
        # This will only work on systems with a /proc file system
        # (like Linux).
        status = open('/proc/self/status')
        for line in status:
            parts = line.split()
            key = parts[0][2:-1].lower()
            if key in result:
                result[key] = int(parts[1])
    finally:
        if status is not None:
            status.close()
    return result


def proc_status(VmKey):
    #scale = {'kB': 1024.0, 'mB': 1024.0*1024.0,
    #         'KB': 1024.0, 'MB': 1024.0*1024.0}
        
    try:
        t = open("/proc/self/status")
        v = t.read()
        t.close()
    except:
        return 0.0  # non-Linux?
    # get VmKey line e.g. 'VmRSS:  9999  kB\n ...'
    i = v.index(VmKey)
    v = v[i:].split(None, 3)  # whitespace
    #if len(v) < 3:
    #    return 0.0  # invalid format?
    # convert Vm value to bytes
    #return float(v[1]) * scale[v[2]]
    #return " ".join(v[1:3])
    return v[1:3]
