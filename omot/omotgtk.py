# -*- coding: utf-8 -*-
"""
MPD client that displays a slide show of images from the song's directory
"""

import sys
import pygtk
pygtk.require('2.0')
import gtk
import glib

from threading import Event, Lock

from omot import resizeable_image
from omot import config
from omot.mpdstatus import mpdstatus
from omot.systools import find_path

from omot.images import images

import logging
logger = logging.getLogger(__name__)


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
    keypress_lock = Event()
    respawn_on_tick = Event()

    def __init__(self):
        config.parse(self.cfg, config.file_parser, 'Display')
        
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

        mpdstatus.connect()
        
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
        else:
            title.append(" [%ds]" % self.cfg["seconds_between_pictures"])
            
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
            
            logger.debug("Updating file list from %s", mpdstatus.covers_dir)
            images.reset_from(mpdstatus.covers_dir)
            return True
        else:
            logger.debug("init: Player stopped or not running")
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
        logger.debug("entering on_tick callback.")
        again = True

        if self.paused:
            logger.debug("Slide show is paused, exiting callback")
            return again

        if self.keypress_lock.is_set():
            logger.debug("Keypress handler is running, exiting callback!")
            return again

        logger.debug("acquring mutex lock...")
        self.mutex.acquire()

        if self.update_file_list():
            # skip to the next picture in list an display it if possible
            self.change_image()
        else:
            logger.debug("Could not get new file list from mpd, exiting callback")

        if self.respawn_on_tick.is_set():
             logger.debug("Spawning new on_tick callback [%ds]" % self.cfg['seconds_between_pictures'])
             glib.timeout_add_seconds(self.cfg['seconds_between_pictures'], self.on_tick)
             again = False
             logger.debug("Callback will be destroyed on exit.")
             self.respawn_on_tick.clear()

        self.update_window_title()
        logger.debug("exiting on_tick callback. releasing mutex lock...")
        self.mutex.release()
        return again

    def on_key_press_event(self, unused_widget, event):
        self.mutex.acquire()
        self.keypress_lock.set()

        pausers  = { "space", "P", "p" }

        quitters = { "Q", "q", "Escape" }
        
        fullscreen_togglers = { "F", "f" }

        skippers = {
                     "Page_Up"   : -1,
                     "Left"      : -1,
                     "Up"        : -1,
                     "k"         : -1,
                     "Page_Down" :  1,
                     "Right"     :  1,
                     "Down"      :  1,
                     "j"         :  1
                   } 

        rotators = { "R" : 90, "r" : 270,
                     "h" : 90, "l" : 270 }
        
        updaters = { "U", "u" }
        
        cache_printers = { "C", "c" }

        delay_modifiers = { "plus": 1, "KP_Add": 1,
                            "minus": -1, "KP_Subtract": -1 }

        keyval = event.keyval
        keyname = gtk.gdk.keyval_name(keyval)
        logger.debug("Key %s (%d) was pressed", keyname, keyval)

        if keyname in pausers:
            self.slideshow_pause_toggle()
        
        elif keyname in quitters:
            logger.info("Quitting.")
            mpdstatus.disconnect()
            gtk.main_quit()
            
        elif keyname in fullscreen_togglers:
            self.fullscreen_toggle()
            
        elif keyname in skippers:
            logger.debug("Skipping picture [%s]", skippers[keyname])
            self.change_image(skippers[keyname])
        
        elif keyname in rotators:
            self.reload_current_image(rotators[keyname])
        
        elif keyname in updaters:
            self.update_file_list() and self.reload_current_image()
            self.update_window_title()
            
        elif keyname in cache_printers:
            images.print_status()

        elif keyname in delay_modifiers:
            logger.debug("Delay: %d" % self.cfg['seconds_between_pictures'])
            if self.cfg['seconds_between_pictures'] + delay_modifiers[keyname] < 1:
                self.cfg['seconds_between_pictures'] = 1
            else:
                self.cfg['seconds_between_pictures'] += delay_modifiers[keyname]
            self.respawn_on_tick.set() # respawn on_tick on next call with new delay
            self.update_window_title() # show new delay setting to user immediately

        self.keypress_lock.clear()
        self.mutex.release()
        return True

    def fullscreen_toggle(self):
        if self.fullscreen:
            logger.info("Exiting fullscreen")
            self.window.unfullscreen()
            self.fullscreen = False
        else:
            logger.info("Going fullscreen")
            self.window.fullscreen()
            self.fullscreen = True

    def slideshow_pause_toggle(self):
        if not self.paused:
            self.paused = True
            self.update_window_title()
            logger.info("Slideshow paused")
        else:
            self.paused = False
            self.update_window_title()
            logger.info("Slideshow unpaused")

