# -*- coding: utf-8 -*-
"""
MPD client to display a slide show of images from the song's directory
"""

import sys
import logging
import time
import pygtk
pygtk.require('2.0')
import gtk
import glib

from threading import Lock

from omot import resizeable_image
from omot import config
from omot.mpdstatus import mpdstatus
from omot.systools import find_path

from omot.images import images


class OmotGtk(object):
    """
    Base application class. Holds these attributes:
    - Configuration
    - A GTK+ window
    - A ResizeableImage nested in the window
    - Window icon pixbuf
    - Some state attributes (paused, lastdir, fullscreen)
    """

    cfg = { 'seconds_between_pictures' : 16,
            'fullscreen'               : False,
            'default_width'            : 1080,
            'default_height'           : 1080,
            'window_title'             : 'Omot',
            'walk_instead_listdir'     : True, # walk is recursive, listdir is not
           }

    paused = False
    lastdir = ""
    fullscreen = False
    mutex = Lock()

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        
        config.parse(self.cfg, config.parser, 'Display')
        
        self.window = gtk.Window()
        if not self.window.get_screen():
            sys.exit("No screen to display window on (check if DISPLAY has been set)!")
        
        self.window.connect('destroy', gtk.main_quit)
        self.window.set_default_size(self.cfg['default_width'], self.cfg['default_height'])
        
        self.icon = gtk.gdk.pixbuf_new_from_file(find_path('blade-runner-331x331.png')) #.scale_simple(256, 256, gtk.gdk.INTERP_HYPER)
        self.window.set_icon(self.icon) #sonatacd.png
        
        self.image = resizeable_image.ResizableImage(True, True, gtk.gdk.INTERP_HYPER)
        self.image.set_from_pixbuf(images.getdefault())
        self.image.show()
        self.window.add(self.image)
        
        self.update_file_list()
        
        self.update_window_title()
        
        self.window.show_all()
        
        if self.cfg['fullscreen']:
            self.fullscreen_toggle()
        
        # connect callbacks
        glib.timeout_add_seconds(self.cfg['seconds_between_pictures'], self.on_tick)
        self.window.connect('key_press_event', self.on_key_press_event)
        
        self.reload_current_image()
    
    def update_window_title(self):
        title = []
        if mpdstatus.playing and mpdstatus.currentsong:
            if mpdstatus.currentsong.get('title') and mpdstatus.currentsong.get('artist'):
                title.append("%s: %s [%s %s] - " 
                             % ( mpdstatus.currentsong.get('artist'),
                                 mpdstatus.currentsong.get('title'),
                                 mpdstatus.currentsong.get('date'),
                                 mpdstatus.currentsong.get('album') ))
            else:
                title.append("%s - " % mpdstatus.currentsong.get('file'))
            
        title.append(self.cfg['window_title'])
        
        if self.paused:
            title.append(' [Paused]')
            
        self.window.set_title(''.join(title))

    def update_file_list(self):
        """
        Tries to get current dir from mpd to reload the files list.
        Clears pixbuf cache on directory change.
        """
        if mpdstatus.update() and mpdstatus.playing and mpdstatus.covers_dir:
            if mpdstatus.covers_dir != self.lastdir:
                if not images.empty:
                    images.clear()
                self.lastdir = mpdstatus.covers_dir
            
            logging.debug("Updating file list from %s", mpdstatus.covers_dir)
            images.reset_from(mpdstatus.covers_dir)
            return True
        else:
            logging.debug("init: Player stopped or not running")
            return False
    
    def reload_current_image(self, rotation = 0):
        pixbuf = images.get_current_pixbuf(rotation)
        self.image.set_from_pixbuf(pixbuf)
        self.window.set_icon(images.get_current_thumbnail())

    def change_image(self, skip = 1):
        # give ResizableImage instance a new pixbuf to display
        pixbuf = images.get_next_pixbuf(skip)
        self.image.set_from_pixbuf(pixbuf)
        self.window.set_icon(pixbuf)
        self.window.set_icon(images.get_current_thumbnail())
        
    def on_tick(self):
        # returning False from on_tick will destroy the timeout
        # and stop calling on_tick
        logging.debug("entering on_tick callback.")

        if self.paused:
            logging.debug("Slide show is paused, exiting callback")
            return True

        logging.debug("acquring mutex lock...")
        self.mutex.acquire()
        
        if self.update_file_list():
            # skip to the next picture in list an display it if possible
            self.change_image()
        else:
            logging.debug("Could not get new file list from mpd, exiting callback")

        self.update_window_title()

        logging.debug("exiting on_tick callback. releasing mutex lock...")
        self.mutex.release()
        return True

    def on_key_press_event(self, unused_widget, event):
        self.mutex.acquire()

        pausers  = { "space", "P", "p" }

        quitters = { "Q", "q", "Escape" }
        
        fullscreen_togglers = { "F", "f" }

        skippers = {
                     "Page_Up"   : -1,
                     "Left"      : -1,
                     "Up"        : -1,
                     "Page_Down" :  1,
                     "Right"     :  1,
                     "Down"      :  1
                   } 

        rotators = { "R" : 90 , "r" : 270 }
        
        updaters = { "U", "u" }
        
        cache_printers = { "C", "c" }

        keyval = event.keyval
        keyname = gtk.gdk.keyval_name(keyval)
        logging.info("Key %s (%d) was pressed", keyname, keyval)

        if keyname in pausers:
            self.slideshow_pause_toggle()
        
        elif keyname in quitters:
            logging.info("Quitting.")
            gtk.main_quit()
            
        elif keyname in fullscreen_togglers:
            self.fullscreen_toggle()
            
        elif keyname in skippers:
            logging.info("Skipping picture [%s]", skippers[keyname])
            self.change_image(skippers[keyname])
        
        elif keyname in rotators:
            self.reload_current_image(rotators[keyname])
        
        elif keyname in updaters:
            self.update_file_list() and self.reload_current_image()
            self.update_window_title()
            
        elif keyname in cache_printers:
            images.print_status()

        self.mutex.release()
        return True

    def fullscreen_toggle(self):
        if self.fullscreen:
            logging.info("Exiting fullscreen")
            self.window.unfullscreen()
            self.fullscreen = False
        else:
            logging.info("Going fullscreen")
            self.window.fullscreen()
            self.fullscreen = True

    def slideshow_pause_toggle(self):
        if not self.paused:
            self.paused = True
            self.update_window_title()
            logging.info("Slideshow paused")
        else:
            self.paused = False
            self.update_window_title()
            logging.info("Slideshow unpaused")

