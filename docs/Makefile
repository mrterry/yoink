# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = build
SOURCEDIR     = source
REPOURL       = git@github.com:mrterry/yoink.git
DOCREPONAME   = yoink_doc
RELEASE       = 0.3

# User-friendly check for sphinx-build
ifeq ($(shell which $(SPHINXBUILD) >/dev/null 2>&1; echo $$?), 1)
$(error The '$(SPHINXBUILD)' command was not found. Make sure you have Sphinx installed, then set the SPHINXBUILD environment variable to point to the full path of the '$(SPHINXBUILD)' executable. Alternatively you can add the directory with the executable to your PATH. If you don't have Sphinx installed, grab it from http://sphinx-doc.org/)
endif

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) source
# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) source

.PHONY: help clean genapi notebooks html dirhtml pickle json htmlhelp latex latexpdf changes linkcheck doctest 

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html       to make standalone HTML files"
	@echo "  dirhtml    to make HTML files named index.html in directories"
	@echo "  pickle     to make pickle files"
	@echo "  json       to make JSON files"
	@echo "  htmlhelp   to make HTML files and a HTML help project"
	@echo "  latex      to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  latexpdf   to make LaTeX files and run them through pdflatex"
	@echo "  changes    to make an overview of all changed/added/deprecated items"
	@echo "  linkcheck  to check all external links for integrity"
	@echo "  doctest    to run all doctests embedded in the documentation (if enabled)"

clean:
	rm -rf $(BUILDDIR)/* && \
	rm source/modules.rst && \
	rm source/yoink.data.rst && \
	rm source/yoink.rst && \
	rm source/notebooks/*.html && \
	rm -rf source/notebooks/html

genapi:
	sphinx-apidoc -f -o source ../yoink

notebooks:
	python make_nb_pages.py source/notebooks/*.ipynb

html: genapi notebooks
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

dirhtml: genapi
	$(SPHINXBUILD) -b dirhtml $(ALLSPHINXOPTS) $(BUILDDIR)/dirhtml
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/dirhtml."

pickle: genapi
	$(SPHINXBUILD) -b pickle $(ALLSPHINXOPTS) $(BUILDDIR)/pickle
	@echo
	@echo "Build finished; now you can process the pickle files."

json: genapi
	$(SPHINXBUILD) -b json $(ALLSPHINXOPTS) $(BUILDDIR)/json
	@echo
	@echo "Build finished; now you can process the JSON files."

htmlhelp: genapi
	$(SPHINXBUILD) -b htmlhelp $(ALLSPHINXOPTS) $(BUILDDIR)/htmlhelp
	@echo
	@echo "Build finished; now you can run HTML Help Workshop with the" \
	      ".hhp project file in $(BUILDDIR)/htmlhelp."

latex: genapi
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex
	@echo
	@echo "Build finished; the LaTeX files are in $(BUILDDIR)/latex."
	@echo "Run \`make' in that directory to run these through (pdf)latex" \
	      "(use \`make latexpdf' here to do that automatically)."

latexpdf: genapi
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex
	@echo "Running LaTeX files through pdflatex..."
	$(MAKE) -C $(BUILDDIR)/latex all-pdf
	@echo "pdflatex finished; the PDF files are in $(BUILDDIR)/latex."

changes: genapi
	$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) $(BUILDDIR)/changes
	@echo
	@echo "The overview file is in $(BUILDDIR)/changes."

linkcheck: genapi
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in $(BUILDDIR)/linkcheck/output.txt."

doctest: genapi
	$(SPHINXBUILD) -b doctest $(ALLSPHINXOPTS) $(BUILDDIR)/doctest
	@echo "Testing of doctests in the sources finished, look at the " \
	      "results in $(BUILDDIR)/doctest/output.txt."
    
push-dev:
	cd $(BUILDDIR) && \
	test -d $(DOCREPONAME) || git clone $(REPOURL) -b gh-pages $(DOCREPONAME) && \
	cd $(DOCREPONAME) && \
	git pull origin gh-pages && \
	test -d dev || mkdir dev && touch dev/_ && \
	rm -r dev/* && \
	cp -r ../html/* dev/ && \
	git add dev/ && \
	git commit -am "Pushed dev docs at $(date)" && \
	git push

push-release:
	cd $(BUILDDIR) && \
	test -d $(DOCREPONAME) || git clone $(REPOURL) -b gh-pages $(DOCREPONAME) && \
	cd $(DOCREPONAME) && \
	git pull origin gh-pages && \
	test -d $(RELEASE) || mkdir $(RELEASE) && touch $(RELEASE)/_ && \
	rm -r $(RELEASE)/* && \
	cp -r ../html/* $(RELEASE)/ && \
	git add $(RELEASE)/ && \
	git commit -am "Pushed $(RELEASE) docs at $(date)" && \
	git push

push-root:
	cd $(BUILDDIR) && \
	test -d $(DOCREPONAME) || git clone $(REPOURL) -b gh-pages $(DOCREPONAME) && \
	cd $(DOCREPONAME) && \
	git pull origin gh-pages && \
	rm -rf libref previous _sources _static *.html *.js *.inv && \
	cp -r ../html/* . && \
	git add . && \
	git commit -am "Pushed root-level docs at $(date)" && \
	git push
