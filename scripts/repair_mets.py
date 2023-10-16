from lxml import etree
from os import path
from glob import glob

#mets_path = "testdata/abel_leibmedicus_1699/mets.xml"
for mets_path in glob('gt_*/data/*/mets.xml'):
    print(mets_path)
    mets = etree.parse(mets_path).getroot()
    mets_changed = False
    for fgroup in mets.xpath('//mets:fileGrp[contains(@USE, "OCR-D-GT")]', namespaces=mets.nsmap):
        to_delete = []
        for file in fgroup.findall('./mets:file', namespaces=mets.nsmap):
            loc = file.find('./mets:FLocat', namespaces=mets.nsmap)
            if loc is None:
                continue
            xmlpath_rel = loc.attrib.get(f'{{{mets.nsmap["xlink"]}}}href', '')
            xmlpath_full = path.join(path.dirname(mets_path), xmlpath_rel)
            if not path.exists(xmlpath_full):
                to_delete.append(file)
                continue
            if xmlpath_rel.endswith(".xml"):
                pagexml = etree.parse(xmlpath_full).getroot()
                pagexml_changed = False
                page = pagexml.find('./*[@imageFilename]')
                img_fname = page.attrib.get('imageFilename', '')
                if img_fname.startswith('../'):
                    img_fname = img_fname[3:]
                    page.attrib['imageFilename'] = img_fname
                    pagexml_changed = True
                img_fullpath = path.join(path.dirname(mets_path), img_fname)
                if not path.exists(img_fullpath):
                    alt_path = path.join('jpg', img_fname)
                    if path.exists(path.join(path.dirname(mets_path), alt_path)):
                        img_fname = alt_path
                        page.attrib['imageFilename'] = img_fname
                        pagexml_changed = True
                if img_fname.endswith('_B.tif'):
                    alt_path = img_fname.replace('_B.tif', '.jpg')
                    if path.exists(path.join(path.dirname(mets_path), alt_path)):
                        img_fname = alt_path
                        page.attrib['imageFilename'] = img_fname
                        pagexml_changed = True
                for other_file in pagexml.findall('.//*[@filename]'):
                    other_file.getparent().remove(other_file)
                    #just remove...
                    #other_fname = other_file.attrib.get("filename", "")
                    #other_path_full = path.join(path.dirname(mets_path), other_fname)
                    #if not path.exists(other_path_full):
                    #    alt_path = path.join('jpg', other_fname)
                    #    if path.exists(path.join(path.dirname(mets_path), alt_path)):
                    #        other_file.attrib["filename"] = alt_path
                    #        pagexml_changed = True
                if pagexml_changed:
                    with open(xmlpath_full, "w") as f:
                        f.write(etree.tounicode(pagexml, doctype='<?xml version="1.0" encoding="UTF-8"?>'))
            if xmlpath_rel.endswith(".xml") and file.attrib.get('MIMETYPE') == "image/jpeg":
                file.attrib["MIMETYPE"] = "application/vnd.prima.page+xml"
                mets_changed = True
        for file in to_delete:
            fgroup.remove(file)
            mets_changed = True
    if mets_changed:
        with open(mets_path, "w") as f:
            f.write(etree.tounicode(mets, doctype='<?xml version="1.0" encoding="UTF-8"?>'))
