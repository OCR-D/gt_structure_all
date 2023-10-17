#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import click
import re
from lxml import etree
from html.parser import HTMLParser

try:
    import magic
except ImportError:
    magic = None


def decode(s, encodings=('ascii', 'utf8', 'latin1')):
    for encoding in encodings:
        try:
            return s.decode(encoding)
        except UnicodeDecodeError:
            pass
    return s.decode('ignore')

def _unicode_escape_replace(match):
    return chr(int("0x%s" % match.group(1),16))

def unicode_escape_replace(s):
    return re.sub(r"&x?([^;]+);", _unicode_escape_replace, s)

class DTATextParser(HTMLParser):
    ignore_tags = ("g")
    treat_as_empty = ("pb", "cb", "hr", "formel")
    # TODO: define block begin: p, cb
    # TODO: ignore text in "<tab></tab>"
    ignore_content_in = ()
    # TODO: marginalia always in own region
    always_own_region = ()
    # TODO: footnotes
    
    def get_page(self, text, page_numbers=[]):
        self.pages = {p_no: etree.Element("Page") for p_no in page_numbers}
        self.onpage = False
        self.pagecount = 0
        self.hanging = []
        self.feed(text)
        return self.pages
    
    def handle_starttag(self, tag, attrs):
        if self.onpage and not any(tag.startswith(x) for x in self.treat_as_empty):
            self.element_stack.append(tag)  # TODO: I guess this should also be active outside of the "onpage" context
        if tag.startswith("pb"):
            self.pagecount += 1
            self.onpage = self.pagecount in self.pages
            self.element_stack = []
            if self.onpage and "=" in tag:
                page_number = tag.split("=")[-1].strip('"')
                self.pages[self.pagecount].attrib["n"] = page_number
        elif self.onpage:
            if tag == "p":
                tr = etree.SubElement(self.pages[self.pagecount], "TextRegion", {"type": "paragraph"})
            elif tag == "kt":
                tr = etree.SubElement(self.pages[self.pagecount], "TextRegion", {"type": "header"})
            elif tag not in self.ignore_tags:
                raise NotImplementedError(f"No handler for start of tag {tag} implemented!")

    def handle_endtag(self, tag):
        if self.onpage and tag in self.element_stack:
            self.element_stack.remove(tag)
        elif not tag.startswith(self.treat_as_empty):
            while self.hanging:  # regions of unknown type at start of page
                tr = self.hanging.pop()
                if tag == "p":
                    tr.attrib["type"] = "paragraph"
                    self.element_stack.append(tag)
                elif tag in ():
                    # TODO: handle other elements over line breaks
                    ...
                else:
                    raise NotImplementedError(f"Hanging text at start of page, no handler for ending tag {tag} implemented!")

    def handle_data(self, data):
        if self.onpage:
            curpage = self.pages[self.pagecount]
            if not len(curpage) and not data.strip():
                return
            if not len(curpage) or not self.element_stack:
                tr = etree.SubElement(curpage, "TextRegion", {"type": "paragraph"})
                self.hanging.append(tr)  # type of this region will be defined in handle_endtag later
            else:
                tr = curpage[-1]
            data = unicode_escape_replace(frac_replace(data))
            tr.text = data if tr.text is None else tr.text + data



@click.command()
@click.option('-p', "--pages", type=click.File('r'), required=True)
@click.argument('text', type=click.File('rb'))
def run(pages, text):

    #
    # the list of pages for which text has to be extracted
    # as a one page per line file
    #
    page_list = []
    for line in pages:
        page_list.append(int((line.strip().split('\t'))[0]))
    page_list = page_list.sort()

    #
    # detect encoding of txt file with magic
    # and convert to string for further proecessing
    #
    if magic is not None:
        m = magic.open(magic.MAGIC_MIME_ENCODING)
        m.load()
        blob = text.read()
        encoding = m.buffer(blob)
        #click.echo(encoding)
        contents = blob.decode(encoding)
    else:
        contents = decode(text.read()).strip()
    
    parser = DTATextParser()
    # print(etree.tounicode(parser.get_page(contents, [28])[28], pretty_print=True))
            

if __name__ == '__main__':
    run()
