from ocrd_utils import VERSION
from ocrd_models.ocrd_page import parse, to_xml, TextEquivType
import xml.etree.ElementTree as ET


def merge(structure_in_path: str, text_in_path: str, out_path: str) -> None:
    """inserts page number, header and paragraph (and other types that might
    appear) from a pseudo-page-xml-file that was generated from a ... text file
    in a page-xml-files text-equivs and writes the page-xml to a file.
    """

    # READ PSEUDO PAGE XML
    tree = ET.parse(text_in_path)

    pseudo_page = tree.getroot()
    print(pseudo_page)
    page_nb = None
    try:
        page_nb = pseudo_page.attrib["n"]
    except:
        print("no page nb")
    pseudo_regions = pseudo_page.findall("TextRegion")
    pseudo_page_regions_by_type = {"header": None, "text": []}
    for pseudo_region in pseudo_regions:
        try:
            pseudo_region.attrib["type"] == "header"
            pseudo_page_regions_by_type["header"] = pseudo_region.text
        except:
            pseudo_page_regions_by_type["text"].append(pseudo_region.text)
    print(pseudo_page_regions_by_type)

    # ---- INSERT IN STRUCTURE PAGE XML -----
    pcgts = parse(inFileName=structure_in_path)
    page = pcgts.get_Page()
    region_types = list(set([region.get_type() for region in page.get_TextRegion()]))
    page_xml_regions_by_type = {}
    for region_type in region_types:
        page_xml_regions_by_type[region_type] = []
    for region in page.get_TextRegion():
        page_xml_regions_by_type[region.get_type()].append(region)

    # sigularize list if only one text region of this type is allowed in page (insert more if required)
    singular_text_region_types = ["page-number", "header"]
    for region_type in singular_text_region_types:
        page_xml_regions_by_type[region_type] = page_xml_regions_by_type[region_type][0]

    # insert page nb,header, etc. if available
    if page_nb:
        page_xml_regions_by_type["page-number"].replace_TextEquiv_at(0, TextEquivType(Unicode=page_nb))
    if pseudo_page_regions_by_type["header"]:
        page_xml_regions_by_type["header"].replace_TextEquiv_at(
            0, TextEquivType(Unicode=pseudo_page_regions_by_type["header"])
        )

    # insert paragraphs
    for i, paragraph in enumerate(page_xml_regions_by_type["paragraph"]):
        paragraph.replace_TextEquiv_at(0, TextEquivType(Unicode=pseudo_page_regions_by_type["text"][i]))

    # write
    with open(out_path, "w") as f:
        f.write(to_xml(pcgts))


# PSEUDO-PAGE and OCR-D-MERGED have to be created
merge(
    structure_in_path="gt_structure_1_1/data/beck_eisen01_1884/GT-PAGE/beck_eisen01_1884_0027.xml",
    text_in_path="gt_structure_1_1/data/beck_eisen01_1884/PSEUDO-PAGE/p27.xml",
    out_path="gt_structure_1_1/data/beck_eisen01_1884/OCR-D-MERGED/beck_eisen01_1884_0027.xml",
)
