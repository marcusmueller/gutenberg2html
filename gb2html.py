#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import lxml.html

from lxml.html  import builder as E
from lxml.html  import tostring as html_string
from cgi        import escape

class GutenbergDownloader :
    gutenberg_url = "http://gutenberg.spiegel.de/buch/{book}/{chapter}"
    chapter_tags  = [ "h2", "h3" ]
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
            chapterselect = doctree.find_class("gbnav")[0]
            self.chapters = [ li[2][ li[2].rfind("/")+1 :] for li in chapterselect.iterlinks() ]

        def __getattr__(self, attr) : 
            return self.info[attr]

    def __init__(self,book) :
        self.book  = book
        url = self.gutenberg_url.format(book=book,chapter=1)
        self.bookinfo = self.BookInfo(self.fetch(url))

    def fetch(self, url) :
        resp = urllib2.urlopen(url)
        html = resp.read()
        return lxml.html.fromstring(html)

    def get_html(self, first = 1, last=-1):
        first = max(0,first)
        if last < 0 :
            last = len(self.bookinfo.chapters)
        else :
            last = max(last,first)
        metas = []
        metas.append(E.META(name="author", value=self.bookinfo.author       ))
        metas.append(E.META(name="DC.title", value=self.bookinfo.title ))
        if hasattr(self.bookinfo, "year") :
            metas.append(E.META(name="date",   value=self.bookinfo.year+"-00-00"))
        htmlbody = E.BODY(E.H1(escape(self.bookinfo.title)))
        target = E.HTML(
            E.HEAD(
                lxml.html.fromstring(
                    "<meta http-equiv=\"content-type\" content=\"text/html; charset=UTF-8\">"
                    ),
                E.TITLE(escape(self.bookinfo.title)),
                *metas
                ),
            htmlbody
            )
        for chap in range(first - 1, last) :
            chapter = self.bookinfo.chapters[chap]
            content = self.fetch(
                self.gutenberg_url.format(
                    book=self.book,
                    chapter = chapter,
                    )
                ).get_element_by_id("gutenb")
            content.set("id","chapter"+chapter)
            for tags in self.chapter_tags : 
                for tag in content.iterchildren(tag=tags) : 
                    tag.set("class","chapter")
            htmlbody.append(content)
        return html_string(target)

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
        "-o","--output",
        help="Output file [default: output to stdout]",
        default="-",
        type=argparse.FileType(mode="w")
        )
    parser.add_argument(
        "-n","--no-output",
        help="Don't output to file or stdout",
        action="store_true"
        )
    parser.add_argument(
        "-b","--browser",
        help="Open generated file in web browser",
        action="store_true"
        )
    parser.add_argument(
        "-r", "--range",
        metavar=("FIRST","LAST"), nargs=2 ,
        type=int,
        help="""read only FIRST to LAST chapters (inclusively).
        Use -1 to denote last chapter.
        Default Behaviour is to get the whole book.
        """,
        )
    return parser.parse_args()

if __name__ == "__main__" :
    args = parse_arguments()
    gutenfetcher = GutenbergDownloader(args.book)
    if args.range :
        res = gutenfetcher.get_html(*args.range)
    else :
        res = gutenfetcher.get_html()
    if not args.no_output:
        args.output.write(res)
        args.output.close()
    if args.browser :
        import webbrowser
        from urllib import pathname2url
        from os.path import abspath
        if not args.no_output:
            url = pathname2url(abspath(args.output.name))
            webbrowser.open(url)
        else :
            from tempfile import NamedTemporaryFile
            tempf = NamedTemporaryFile(suffix=".html", prefix="book"+str(args.book)+"_",
                    mode="w", delete=False)
            tempf.write(res)
            tempf.flush()
            url = pathname2url(abspath(tempf.name))
            webbrowser.open(url)
            tempf.close()
