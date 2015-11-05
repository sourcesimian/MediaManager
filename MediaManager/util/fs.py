import os

def available_space(path):
    # statvfs = os.statvfs('/home/foo/bar/baz')
    #
    # statvfs.f_frsize * statvfs.f_blocks     # Size of filesystem in bytes
    # statvfs.f_frsize * statvfs.f_bfree      # Actual number of free bytes
    # statvfs.f_frsize * statvfs.f_bavail     # Number of free bytes that ordinary users
    #                                       # are allowed to use (excl. reserved space)
    statvfs = os.statvfs(path)
    return statvfs.f_frsize * statvfs.f_bavail