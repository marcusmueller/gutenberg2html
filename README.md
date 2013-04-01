gutenberg2html
==============

Download books from Projekt Gutenberg-DE (http://gutenberg.spiegel.de/) and compile them into a single HTML file.

Also adds `class="chapter"` to `<h2>`s, for later conversion and automatic formatting via CSS.

Usage
-----


			usage: gb2html.py [-h] [-r FIRST LAST] book

			positional arguments:
			  book                  Number of desired Gutenberg-DE book (uint)

			optional arguments:
			  -h, --help            show this help message and exit
			  -r FIRST LAST, --range FIRST LAST
						read only FIRST to LAST chapters (inclusively). Use -1
						to denote last chapter. Default Behaviour is to get
						the whole book.

			Urls follow the scheme http://gutenberg.spiegel.de/buch/{book}/{chapter}.
