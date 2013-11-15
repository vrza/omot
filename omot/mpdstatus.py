"""
Module that defines and instantiates a class that holds
mpd status info, and methods for fetching that status info from mpd
"""

import os
import time

from mpd import MPDClient, CommandError, ConnectionError
from socket import error as SocketError

from omot import config
from omot.mytools import infer_covers_dir

import logging
logger = logging.getLogger(__name__)


class MpdStatus(object):
    """
    Holds information about status of mpd, 
    uses a MPDClient instance to update itself
    """
    
    cfg = { 'host'            : 'localhost',
            'port'            : '6600',
            'music_directory' : '/var/lib/mpd/music/',
            'password'        : ''
          }

    def __init__(self):
        self.covers_dir  = None # string (path to a directory)
        self.currentsong = None
        self._state      = None # string, e.g. 'play'
        self._client     = MPDClient(use_unicode=True)
        self._connected  = False

        # Parse 'MPD' section of configuration file
        config.parse(self.cfg, config.file_parser, 'MPD')

    def connect(self):
        """
        Try to connect to mpd
        """
        logger.debug('Trying to connect to mpd at %s:%s...',
                     self.cfg['host'], self.cfg['port'])
        start = time.time()
        if self._mpd_connect(self.cfg['host'], self.cfg['port']):
            logger.info('Connected to mpd at %s:%s!',
                         self.cfg['host'], self.cfg['port'])
        else:
            logger.error("Failed to connect to mpd! [after %s seconds]",
                          str(time.time() - start) )
            return False

        if self.cfg['password']:
            if self._mpd_auth(self.cfg['password']):
                logger.info('Pass auth!')
            else:
                logger.error(
                    "Error trying to pass auth. [after %s seconds]",
                    str(time.time() - start))
                self._client.disconnect()
                return False

        self._connected = True
        return

    def disconnect(self):
        self._client.close()
        self._client.disconnect()
        self._connected = False
        return

    def update(self):
        start = time.time()
        if not self._connected:
            # reconnect or bust
            if not self.connect():
                return False

        # update playing state
        # TODO: connection could still be broken
        try:
            self._state = self._client.status().get('state')
        except ConnectionError:
            logger.error("Connection error.")
            self._connected = False
            return False

        # get current song path and infer covers dir from it
        self.currentsong = self._client.currentsong()
        currentfile = self.currentsong.get('file')
        if self.currentsong and currentfile:
            # infer absolute covers directory path
            logger.debug("Currently playing: %s", currentfile)
            covers_dir_relative = infer_covers_dir(currentfile)
            logger.debug("Guessing covers dir: %s", covers_dir_relative)
            self.covers_dir = os.path.join(self.cfg['music_directory'],
                                           covers_dir_relative)
        else:
            self.covers_dir = None

        logger.debug("mpd status update took %s seconds",
                     str(time.time() - start))
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
