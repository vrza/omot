"""
Module that defines and instantiates a class that holds
mpd status info, and methods for fetching that status info from mpd
"""

import os
import logging
import time

from mpd import MPDClient, CommandError
from socket import error as SocketError

from omot import config
from omot.mytools import infer_covers_dir

class MpdStatus(object):
    """
    Holds information about status of mpd, 
    uses a MPDClient instance to update itself
    """
    
    cfg = { 'host'      : 'localhost',
            'port'      : '6600',
            'music_dir' : '/var/lib/mpd/music/',
            'password'  : ''
          }

    def __init__(self):
        self.covers_dir = None # string (path to a directory)
        self._state     = None # string, e.g. 'play'
        self._client = MPDClient()

        # Parse 'MPD' section of configuration file
        config.parse(self.cfg, config.parser, 'MPD')
        
    def update(self):
        """
        Try to connect to mpd to update playing state and covers_dir
        """

        logging.info('Trying to connect to mpd at %s:%s...',
                     self.cfg['host'], self.cfg['port'])
        start = time.time()

        if self._mpd_connect(self.cfg['host'], self.cfg['port']):
            logging.info('Connected to mpd!')
        else:
            logging.error("Failed to connect to mpd! [after %s seconds]",
                          str(time.time() - start) )
            return False

        if self.cfg['password']:
            if self._mpd_auth(self.cfg['password']):
                logging.info('Pass auth!')
            else:
                logging.error(
                    "Error trying to pass auth. [after %s seconds]",
                    str(time.time() - start))
                self._client.disconnect()
                return False

        # update playing state 
        self._state = self._client.status().get('state')

        # infer absolute covers directory path
        currentfile = self._client.currentsong().get('file')
        if currentfile:
            logging.info("Currently playing: %s", currentfile)
            covers_dir_relative = infer_covers_dir(currentfile)
            logging.info("Guessing covers dir: %s", covers_dir_relative)
            self.covers_dir = os.path.join(self.cfg['music_dir'], 
                                           covers_dir_relative)
        else:
            self.covers_dir = None

        logging.info("mpd status update took %s seconds",
                     str(time.time() - start))
        self._client.disconnect()
        return self.covers_dir is not None

    @property
    def playing(self):
        """
        Is mpd playing? 
        """
        return self._state == 'play'
        
    def _mpd_connect(self, host, port):
        """
        Simple wrapper to connect MPD.
        """
        try:
            self._client.connect(host, port)
        except SocketError:
            return False
        return True
    
    def _mpd_auth(self, secret):
        """
        Authenticate
        """
        try:
            self._client.password(secret)
        except CommandError:
            return False
        return True


# instantiate
mpdstatus = MpdStatus()
