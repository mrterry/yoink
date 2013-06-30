from setuptools import setup

setup(
    name='yoink',
    version='0.2',
    description='Yoinking data from rasterized images',
    author='Matt Terry',
    author_email='matt.terry@gmail.com',
    url='https://github.com/mrterry/yoink',
    packages=['yoink'],
    package_data={'yoink': ['data/*.png']},
    scripts=['bin/yoink_cmap',
             'bin/yoink_points',
             ],
    install_requires=['numpy', 'scipy', 'scikit-image', 'matplotlib >= 1.2'],
)
