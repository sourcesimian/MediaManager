#! /usr/bin/env python

"""\
%prog [options]
"""

import os

from MediaManager.audio.library.tree import TreeLibrary
from MediaManager.audio.synclist import SyncList, SyncSelect
from MediaManager.audio.library.flat import FlatLibrary
from MediaManager.audio.library.albumart import AlbumArtLibrary
from MediaManager.audio.library.info import InfoLibrary


def update_sync_list(from_lib, to_lib, sync_file):
    sync_list = SyncList(sync_file).load()
    sync_select = SyncSelect(from_lib, to_lib, sync_list)
    if sync_select.show_selection_window():
        print "- Writing: %s" % sync_file
        sync_list.save()
        return True
    return False


def sync_albums(from_lib, to_lib, sync_file, album_art):
    sync_list = SyncList(sync_file).load()

    for name in sync_list:
        if sync_list[name] == '-':
            print "- %s" % name
            to_lib.delete_album(name)

    for name in sync_list:
        if sync_list[name] == '+':
            if to_lib.has_album(name):
                continue
            if not from_lib.has_album(name):
                continue
            print "+ %s" % name
            album = from_lib.get_album(name)
            to_lib.add_album(album, album_art)


def diff(from_lib, to_lib):
    src = {album.name for album in from_lib}
    dst = {album.name for album in to_lib}

    diff = []
    for name in src - dst:
        diff.append(('+', name))

    for name in dst - src:
        diff.append(('#', name))

    def by_name(a, b):
        return cmp(a[1], b[1])

    diff.sort(by_name)

    for state, name in diff:
        print '%s %s' % (state, name)


def list_albums(from_lib):
    for album in sorted(from_lib):
        print album.name


def main():
    from argparse import ArgumentParser

    arg_parser = ArgumentParser()
    arg_parser.add_argument('from_lib', help='Source archive folder (TreeLibrary)')
    arg_parser.add_argument('to_lib', nargs='?', help='Destination folder (FlatLibrary)', default=None)
    arg_parser.add_argument('--cache', help='Online album art cache folder')
    arg_parser.add_argument('--list', help='Sync-list file [<to_lib>/sync.diff]')
    arg_parser.add_argument('--sync-now', help='Skip the selection window', action="store_true")
    arg_parser.add_argument('--select-only', help='Only generate sync-list', action="store_true")
    arg_parser.add_argument('--diff', help='Difference between the libraries', action="store_true")

    args = arg_parser.parse_args()

    if args.sync_now and args.select_only:
        arg_parser.error('Can\'t choose both: --sync-now and --select-only')

    from_lib = TreeLibrary(args.from_lib)
    if args.to_lib:
        to_lib = FlatLibrary(args.to_lib)
    elif args.list:
        to_lib = InfoLibrary()

    sync_file = args.list
    if not sync_file and args.to_lib:
        sync_file = os.path.join(args.to_lib, "sync.diff")

    album_art = None
    if args.cache:
        album_art = AlbumArtLibrary(args.cache, False)

    if args.to_lib:
        if args.sync_now:
            sync_albums(from_lib, to_lib, sync_file, album_art)
        elif args.diff:
            diff(from_lib, to_lib)
        elif args.to_lib:
            if update_sync_list(from_lib, to_lib, sync_file):
                if not args.select_only:
                    sync_albums(from_lib, to_lib, sync_file, album_art)
    else:
        list_albums(from_lib)

if __name__ == '__main__':
    main()
