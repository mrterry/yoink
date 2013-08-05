from distutils.core import setup

descr = """Data Extraction Tools

Yoink is a tool for extracting data from rasterized images.  It currently
supports interactively picking points from line plots.  It also supports
extracting the scalar field from a colormapped image.  Yoink builds on top
matplotlib and is platform and rendering backend independent.

Please refer to the online documentation at http://yoinkery.com/

Follow development at https://github.com/mrterry/yoink
"""

DISTNAME = 'yoinkery'
DESCRIPTION = 'Yoinking data from rasterized images'
LONG_DESCRIPTION = descr
MAINTAINER = 'Matt Terry'
MAINTAINER_EMAIL = 'matt.terry@gmail.com'
URL = 'http://yoinkery.com'
LICENSE = 'Modified BSD'
VERSION = '0.3'

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: Implementation :: CPython',
    'Topic :: Scientific/Engineering :: Visualization',
    'Topic :: Utilities',
]

setup(
    name=DISTNAME,
    version=VERSION,
    author='Matt Terry',
    author_email='matt.terry@gmail.com',
    license=LICENSE,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    platform='Any',
    hidden=True,
    classifiers=CLASSIFIERS,
    url=URL,
    packages=['yoink', 'yoink.data', 'yoink.test'],
    package_data={'yoink': ['data/*.png', 'test/*.txt']},
    scripts=['bin/yoink'],
    install_requires=['numpy', 'scipy', 'matplotlib >= 1.2'],
    requires=['numpy', 'scipy', 'matplotlib'],
    include_package_data=True,
)
