#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#


def configure_logging():
    import logging
    from omot import config
    if config.options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    configure_logging()
    import pygtk
    pygtk.require('2.0')
    import gtk
    from omot import omotgtk
    omotgtk.OmotGtk()
    gtk.main()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
