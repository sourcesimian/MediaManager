# MediaManager
Audio Collection Manager


## Music Sync
MediaManager transforms an unstructured music archive with irregular path, file,
ID3 tags and album art into a normalised folder of albums with minimal effort.
MM will not modify your music archive, it reads your archive and outputs to a new
location. To use MM all you need to do is touch a .album file into the base folder
of each one of your albums and MM can do most of the rest of the work.If MM does
not get it completely right you can force by adding 'artist', 'title' attributes.

Sample .album file with attributes:

    artist =
    title = 90's Summer hits

Sample Usage:

    Manage jogging albums list:
      $ mm-sync-music ~/Music/archive --list ./jogging.diff

    Push your jogging music onto USB
      $ mm-sync-music ~/Music/archive /media/usb --list ./jogging.diff --sync-now

    Add and remove albums on USB
      $ mm-sync-music ~/Music/archive /media/usb
      # list will default to /media/usb/sync.diff

     Or just make selections:
      $ mm-sync-music ~/Music/archive /media/usb --select-only

     Skip selection window and make it so:
      $ mm-sync-music ~/Music/archive /media/usb --sync-now

     Sync with GoogleImages lookups for missing album art:
      $ mm-sync-music ~/Music/archive /media/usb --sync-now --cache ~/Downloads/album_arts

## Install
    pip install https://github.com/sourcesimian/MediaManager/tarball/v0.0.1#egg=MediaManager-0.0.1 --process-dependency-links
    