Directions for deploying to github pages
----------------------------------------

$ cd $YOINK_REPO/docs

update the doc pages by running
$ make html

commit the new docs to gh-pages branch
$ python gh-pages.py

push the changes to github for serving
$ cd gh-pages
$ git push origin gh-pages
