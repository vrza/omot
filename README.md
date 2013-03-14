Omot
====

Connects to local MPD service and displays a slide show of album cover images
associated with currently played file.

Configuration
-------------

Configuration is read from `~/.omotrc` or `~/.omot`. Example configuration:

    [Display]
    seconds_between_pictures = 5
    fullscreen               = False
    window_title             = Omotljika
    default_width            = 1200
    default_height           = 943

    [MPD]
    music_dir                = /var/lib/mpd/music
    host                     = 127.0.0.1
    port                     = 6600
