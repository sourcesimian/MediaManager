from setuptools import setup, find_packages

setup(
    name='MediaManager',
    packages=find_packages(exclude=['tests']),
    version='0.1',
    description='Media collection manager',
    author='Source Simian',
    install_requires=['mutagen'],
    entry_points={
        "console_scripts": [
            "mm-music-sync=MediaManager.cli.music_sync:main",
        ]
    }
)
