Omot
====

Connects to local MPD service and displays a slide show of album cover images
associated with currently played file.

Configuration
-------------

Omot looks for configuration files `~/.omotrc` and `~/.omot`, in that order.
Example configuration file:

    [Display]
    seconds_between_pictures = 5
    fullscreen               = False
    window_title             = Omotljika
    default_width            = 1200
    default_height           = 943

    [MPD]
    music_directory          = /var/lib/mpd/music
    host                     = 127.0.0.1
    port                     = 6600
