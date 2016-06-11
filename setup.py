from setuptools import setup, find_packages

setup(
    name='MediaManager',
    version="0.0.1",
    download_url="https://github.com/sourcesimian/MediaManager/tarball/v0.0.1",
    url='https://github.com/sourcesimian/pyVpnPorthole',
    description='Media collection manager',
    author='Source Simian',
    author_email='sourcesimian@users.noreply.github.com',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    install_requires=['mutagen'],
    entry_points={
        "console_scripts": [
            "mm-music-sync=MediaManager.cli.music_sync:main",
        ]
    }
)
