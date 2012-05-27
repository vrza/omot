"""
This module defines methods for config file parsing
and creates an instance of RawConfigParser
"""

import os
import logging
import ConfigParser

def parse(mem, disk, section):
    """ Update fields defined in hashmap 'mem' from ConfigParser 'disk'
        Fields are updated only if their values in config file match the
        value types in 'mem' hashmap.
        Example:
        mem = { 'seconds_between_pictures' : 16,
                'fullscreen'               : False,
                'default_width'            : 1080,
                'default_height'           : 1080,
                'window_title'             : 'Omot',
                'walk_instead_listdir'     : True,  # walk is recursive, listdir is not
              }
        disk = ConfigParser.RawConfigParser()
        disk.read(os.path.expanduser('~/.omot'))
        parse (mem, disk, 'Display')
    """
    
    if not disk.has_section(section):
        return
        
    for key in mem:
        if disk.has_option(section, key):
            try:
                if isinstance(mem[key], bool):
                    mem[key] = disk.getboolean(section, key)
                elif isinstance(mem[key], int):
                    mem[key] = disk.getint(section, key)
                elif isinstance(mem[key], str):
                    mem[key] = disk.get(section, key)
            except ValueError:
                logging.error("Bad value in %s section: %s, should be of %s", 
                              section, key, type(mem[key]))
    
    return mem


# instantiate parser and read config file
parser = ConfigParser.RawConfigParser()
for candidate in ['~/.omotrc', '~/.omot']:
    if parser.read(os.path.expanduser(candidate)):
        break


# Configuration file writing example:
# >>> config.add_section('Display')
# >>> config.set('Display', 'seconds_between_pictures', SECONDS_BETWEEN_PICTURES)
# >>> config.set('Display', 'fullscreen', FULLSCREEN)
# >>> config.set('Display', 'walk_instead_listdir', WALK_INSTEAD_LISTDIR)
# >>> with open(os.path.expanduser('~/.mpdcover'), 'wb') as configfile:
# ...     config.write(configfile)
