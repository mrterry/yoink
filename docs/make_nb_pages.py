import os
from os.path import join as pjoin
from subprocess import check_call
import argparse

template = """\
.. raw:: html
   :file: {html_path}
"""


def make_notebook_page(nb_path):
    """Convert ipython notebooks to useful stubs for sphinx

    from    /path/to/FILE.ipynb
    create  /path/to/FILE.rst
            /path/to/html/FILE.html
    """
    assert nb_path[-6:] == '.ipynb'
    dirname, filename = os.path.split(nb_path)
    prefix = filename[:-6]
    html_path = pjoin(dirname, 'html', prefix+'.html')
    rst_path = pjoin(dirname, 'nb', prefix+'.rst')

    try:
        os.mkdir(pjoin(dirname, 'html'))
    except OSError:
        pass

    try:
        os.mkdir(pjoin(dirname, 'nb'))
    except OSError:
        pass

    with open(html_path, 'w') as f:
        cmd = ['ipython nbconvert --format=full_html --stdout ' + nb_path]
        check_call(cmd, stdout=f, shell=True)

    with open(rst_path, 'w') as f:
        f.write(template.format(html_path=os.path.abspath(html_path)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='generate sphinx boilerplate for ipynb files')
    parser.add_argument('nb_paths', nargs='+', help='files to process')

    args = parser.parse_args()
    for path in args.nb_paths:
        make_notebook_page(path)
