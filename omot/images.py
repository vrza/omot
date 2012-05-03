'''
Created on May 2, 2012

@author: random
'''
import os
import time

import logging

import pygtk
pygtk.require('2.0')
import gtk

import gc

from omot.cache import Cache
from omot.systools import find_path
from omot.systools import proc_status


class Images(Cache):
    """
    Provides on-demand caching of pixbufs backed by files on disk.

    Holds these attributes (all private):
    - A list of image files and a pointer to that list
    - Object cache (from base class):
      filename path strings are keys, pixbuf objects are values
    - A list of acceptable image file extensions
    """
    index = 0
    files = []
    acceptable_image_suffixes = []
    defaultpixbuf = None

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        
        # get supported image formats from GTK+
        self.acceptable_image_suffixes = [ext for fmt in gtk.gdk.pixbuf_get_formats() for ext in fmt['extensions']]
        logging.info("Acceptable extensions: %s", self.acceptable_image_suffixes)
        
        # default image
        self.defaultpixbuf = gtk.gdk.pixbuf_new_from_file(find_path('blade-runner.jpg'))

    def setdefault(self, pixbuf):
        self.defaultpixbuf = pixbuf

    def getdefault(self):
        return self.defaultpixbuf

    def clear(self):
        prevrss = int(proc_status('VmRSS')[0])
        logging.info("Clearing object cache: %s", self.cache)
        super(Images, self).clear()
        logging.info("Running garbage collection...")
        start = time.time()
        gc.collect()
        logging.info("Garbage collection took %s seconds", time.time() - start)
        logging.info("Resource usage before: %d kB", prevrss)
        logging.info("Resource usage after: %s kB", proc_status('VmRSS')[0])
        logging.info("Freed %d kB of resident memory", prevrss - int(proc_status('VmRSS')[0]))  

    def is_readable_image(self, filename):
        """
        Returns True if argument is a name of an existing file and if
        that file's extension is listed in self.acceptable_image_suffixes
        """
        if not os.path.isfile(filename):
            logging.info("Is not file: %s", filename)
            return False
        
        for suffix in self.acceptable_image_suffixes:
            if filename.lower().endswith(suffix):
                return True
        
        return False

    def find_image_files(self, location, recursive = True):
        """
        Finds all image files in location directory, and
        reinitializes self.files list
        """
        file_list = []
        logging.info("Looking for image file_entries in: %s", location)
        start = time.time()
        if recursive:
            for directory, unused_subdir_entries, file_entries in os.walk(location):
                for filename in file_entries:
                    filepath = os.path.join(directory, filename)
                    if self.is_readable_image(filepath):
                        file_list.append(filepath)
        else:
            for filename in os.listdir(location):
                filepath = os.path.join(location, filename)
                if self.is_readable_image(filepath):
                    file_list.append(filepath)

        logging.info("Found %d images in %s seconds: %s", len(file_list), time.time() - start, str(file_list))
        return file_list
    

    def reset_from(self, location, recursive = True):
        self.files = self.find_image_files(location, recursive)
        
    def add_from(self, location, recursive = True):
        for filename in self.find_image_files(location, recursive):
            self.files.append(filename)
    
    def get_pixbuf(self, skip = 1, rotation = 0):
        if not self.files:
            if rotation:
                self.defaultpixbuf = self.defaultpixbuf.rotate_simple(rotation)
            return self.defaultpixbuf
        
        self.index = (self.index + skip) % len(self.files)
        
        filename = self.files[self.index]
        logging.info("Trying to get [%d] %s", self.index, filename)
        
        assert self.is_readable_image(filename)
        
        # check cache
        cache_hit = self.has(filename)
        if cache_hit:
            logging.info("Image cache hit :o)")
            pixbuf = self.get(filename)
        else:
            logging.info("Image cache miss, loading image from disk...")
            start = time.time()
            pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
            logging.info("Loaded image in %s seconds", time.time() - start)
        
        # apply rotation (optional)
        if rotation:
            logging.info("Rotating by %d degrees (ccw): %s...", rotation, filename)
            pixbuf = pixbuf.rotate_simple(rotation)
        
        if rotation or not cache_hit:
            self.put(filename, pixbuf)
            logging.info("Image cache has %i pixbufs", self.size)
        
        # give ResizableImage instance a new pixbuf to display
        return pixbuf

    def print_status(self):
        super(Images, self).print_keys()
        print "RSS: %s" % proc_status('VmRSS')


# instantiate
images = Images()