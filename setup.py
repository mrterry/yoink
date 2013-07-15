from textwrap import dedent

VERSION = '0.2dev'

classifiers = dedent("""\
    Development Status :: 3 - Alpha
    Intended Audience :: Science/Research
    License :: OSI Approved :: BSD License
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: 3.3
    Programming Language :: Python :: Implementation :: CPython
    Topic :: Scientific/Engineering :: Visualization
    Topic :: Utilities""")

description = dedent("""\
    Yoink is a tool for extracting data from rasterized images.  It currently
    supports interactively picking points from line plots.  It also supports
    extracting the scalar field from a colormapped image.  Yoink builds on top
    matplotlib and is platform and rendering backend independent.""")

from setuptools import setup

setup(
    name='yoink',
    version=VERSION,
    author='Matt Terry',
    author_email='matt.terry@gmail.com',
    home_page=None,
    license='BSD',
    summary='Yoinking data from rasterized images',
    description=description,
    platform='Any',
    hidden=True,
    classifiers=classifiers,
    url='https://github.com/mrterry/yoink',
    packages=['yoink'],
    package_data={'yoink': ['data/*.png']},
    scripts=['bin/yoink'],
    install_requires=['numpy', 'scipy', 'matplotlib >= 1.2'],
)
