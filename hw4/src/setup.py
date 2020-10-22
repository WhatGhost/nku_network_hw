from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('client.py', base=base),
	Executable('server.py', base=base),
]

setup(name='nethw4',
      version = '1.0',
      description = 'gyy2120190419',
      options = dict(build_exe = buildOptions),
      executables = executables)
