from setuptools import setup

config = {
    'app': ['crossover_trial_extender.py'],
    'data_files': [],
    'options': {
        'py2app': {
            'argv_emulation': False,
            'packages': [],
            'iconfile': '.media/icon.icns',
        }
    },
    'setup_requires': ['py2app'],
}

setup(**config)
