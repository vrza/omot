'''
Created on May 2, 2012

@author: random
'''
import os
import time

import pygtk
pygtk.require('2.0')
import gtk

import gc

from omot.cache import Cache
from omot.systools import find_path
from omot.systools import proc_status

import logging
logger = logging.getLogger(__name__)


class Images(Cache):
    """
    Provides on-demand caching of pixbufs backed by files on disk.

    Holds these attributes (all private):
    - A list of image files and a pointer to that list
    - Object cache (from base class):
      filename path strings are keys, pixbuf objects are values
    - A list of acceptable image file extensions
    """

    def __init__(self):
        self.files = []
        self.index = 0

        # get supported image formats from GTK+
        self.acceptable_image_suffixes = [ext for fmt in gtk.gdk.pixbuf_get_formats() for ext in fmt['extensions']]
        logger.debug("Acceptable extensions: %s", self.acceptable_image_suffixes)
        
        # default image
        self.defaultpixbuf = gtk.gdk.pixbuf_new_from_file(find_path('blade-runner.jpg'))

    def setdefault(self, pixbuf):
        self.defaultpixbuf = pixbuf

    def getdefault(self):
        return self.defaultpixbuf

    def clear(self):
        prevrss = int(proc_status('VmRSS')[0])
        logger.debug("Clearing object cache: %s", self.cache)
        super(Images, self).clear()
        logger.debug("Running garbage collection...")
        start = time.time()
        gc.collect()
        logger.debug("Garbage collection took %s seconds", time.time() - start)
        logger.debug("Resource usage before: %d kB", prevrss)
        logger.debug("Resource usage after: %s kB", proc_status('VmRSS')[0])
        logger.debug("Freed %d kB of resident memory", prevrss - int(proc_status('VmRSS')[0]))

    def is_readable_image(self, filename):
        """
        Returns True if argument is a name of an existing file and if
        that file's extension is listed in self.acceptable_image_suffixes
        """
        if not os.path.isfile(filename):
            logger.error("Is not file: %s", filename)
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
        logger.debug("Looking for image file_entries in: %s", location)
        start = time.time()
        if recursive:
            for directory, unused_subdir_entries, file_entries in os.walk(location, True, None, True):
                for filename in file_entries:
                    filepath = os.path.join(directory, filename)
                    if self.is_readable_image(filepath):
                        file_list.append(filepath)
        else:
            for filename in os.listdir(location):
                filepath = os.path.join(location, filename)
                if self.is_readable_image(filepath):
                    file_list.append(filepath)

        logger.debug("Found %d images in %s seconds: %s", len(file_list), time.time() - start, str(file_list))
        return file_list
    
    def reset_from(self, location, recursive = True):
        self.files = self.find_image_files(location, recursive)
        
    def add_from(self, location, recursive = True):
        for filename in self.find_image_files(location, recursive):
            self.files.append(filename)
            
    def get_next_pixbuf(self, skip = 1, rotation = 0):
        if self.files:
            self.index = (self.index + skip) % len(self.files)
        return self.get_current_pixbuf(rotation)     
    
    def get_current_pixbuf(self, rotation = 0):
        if not self.files:
            if rotation:
                self.defaultpixbuf = self.defaultpixbuf.rotate_simple(rotation)
            return self.defaultpixbuf
        
        filename = self.files[self.index]
        logger.debug("Trying to get [%d] %s", self.index, filename)
        
        assert self.is_readable_image(filename)
        
        # check cache
        cache_hit = self.has(filename)
        if cache_hit:
            logger.debug("Image cache hit :o)")
            pixbuf = self.get(filename)
        else:
            logger.debug("Image cache miss, loading image from disk...")
            start = time.time()
            pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
            logger.debug("Loaded image in %s seconds", time.time() - start)
        
        # apply rotation (optional)
        if rotation:
            logger.debug("Rotating by %d degrees (ccw): %s...", rotation, filename)
            pixbuf = pixbuf.rotate_simple(rotation)
        
        if rotation or not cache_hit:
            # store new pixmap in the cache
            self.put(filename, pixbuf)
            logger.debug("Image cache has %i pixbufs", self.size)
            
            # also update its thumb
            logger.debug("Creating icon...")
            start = time.time()
            self.put("t_" + filename, pixbuf.scale_simple(64, 64, gtk.gdk.INTERP_NEAREST))
            logger.debug("Generated icon in %s seconds", time.time() - start)
        
        # give ResizableImage instance a new pixbuf to display
        return pixbuf

    def get_current_thumbnail(self):
        if not self.files:
            return self.defaultpixbuf
        return self.get("t_" + self.files[self.index])

    def print_status(self):
        super(Images, self).print_keys()
        logger.info( "RSS: %s", proc_status('VmRSS'))


# instantiate
images = Images()