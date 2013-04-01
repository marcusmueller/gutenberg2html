#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import lxml.html

from lxml.html  import builder as E
from lxml.html  import tostring as html_string
from cgi        import escape

class GutenbergDownloader :
    gutenberg_url = "http://gutenberg.spiegel.de/buch/{book}/{chapter}"
    class BookInfo:
        def __init__(self, doctree) :
            metadata_div = doctree.get_element_by_id("metadata")
            metadata_table = metadata_div[0]
            trs = metadata_table.iterchildren(tag="tr")
            self.info = dict()
            for tr in trs:
                key   = tr[0].text_content()
                value = tr[1].text_content()
                self.info[key]=value
                ##we take the detour via a special dict
                ##instead of vars(self) for security reasons
                ##(one could do funny stuff by manipulating things
                ##like inserting __del__ into the table...aaaa)
            chapterselect = doctree.get_element_by_id("chapters")
            self.chapters =[opt.get("value")  for opt in chapterselect.iterchildren(tag="option") ]

        def __getattr__(self, attr) : 
            return self.info[attr]

    def __init__(self,book, first = 1, last = -1) :
        self.book  = book
        self.first = first
        url = self.gutenberg_url.format(book=book,chapter=1)
        self.bookinfo = self.BookInfo(self.fetch(url))
        if last < 0 :
            self.last = len(self.bookinfo.chapters)
        else :
            self.last = max(last,first)
        metas = []
        metas.append(E.META(name="author", value=self.bookinfo.author       ))
        metas.append(E.META(name="booktitle", value=self.bookinfo.booktitle ))
        metas.append(E.META(name="date",   value=self.bookinfo.year+"-00-00"))
        self.htmlbody = E.BODY(E.H1(escape(self.bookinfo.title)))
        self.target = E.HTML(
            E.HEAD(
                lxml.html.fromstring(
                    "<meta http-equiv=\"content-type\" content=\"text/html; charset=UTF-8\">"
                    ),
                E.TITLE(escape(self.bookinfo.title)),
                *metas
                ),
            self.htmlbody
            )
        for chap in range(self.first - 1, self.last) :
            content = self.fetch(
                self.gutenberg_url.format(
                    book=self.book,
                    chapter = self.bookinfo.chapters[chap]
                    )
                ).get_element_by_id("gutenb")
            for h2 in content.iterchildren(tag="h2") : 
                h2.set("class","chapter")
            self.htmlbody.append(content)
#        html_string(self.target)
        lxml.html.open_in_browser(self.target)

    def fetch(self, url) :
        resp = urllib2.urlopen(url)
        html = resp.read()
        return lxml.html.fromstring(html)

def parse_arguments() :
    import argparse
    parser = argparse.ArgumentParser(
        epilog="Urls follow the scheme "+GutenbergDownloader.gutenberg_url+"."
        )
    parser.add_argument(
        "book",
        help="Number of desired Gutenberg-DE book (uint)",
        type=lambda inp : abs(int(inp))
        )
    parser.add_argument(
        "-r", "--range",
        metavar=("FIRST","LAST"), nargs=2 ,
        type=lambda inp : abs(int(inp)),
        help="""read only FIRST to LAST chapters (inclusively).
        Use -1 to denote last chapter.
        Default Behaviour is to get the whole book.
        """,
        )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    if args.range :
        gutenfetcher = GutenbergDownloader(args.book, **args.range)
    else :
        gutenfetcher = GutenbergDownloader(args.book)
