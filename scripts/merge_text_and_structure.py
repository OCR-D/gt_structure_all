from ocrd_models.ocrd_page import parse, to_xml, TextEquivType
import xml.etree.ElementTree as ET


def merge(gt_structure_path: str, gt_text_path: str, out_path: str) -> None:
    """inserts page number, header and paragraph (and other types that might
    appear) from a pseudo-page-xml-file that was generated from a ... text file
    in a page-xml-files text-equivs and writes the page-xml to a file.
    """

    # --- READ GT-TEXT-PSEUDO-PAGE-XML
    tree = ET.parse(gt_text_path)
    pseudo_page = tree.getroot()
    page_nb = pseudo_page.attrib.get("n")
    pseudo_regions = pseudo_page.findall("TextRegion")
    # add other region types here as needed
    pseudo_page_regions_dict = {"header": None, "text": []}
    for pseudo_region in pseudo_regions:
        region_type = pseudo_region.attrib.get("type")
        if region_type == "header":
            pseudo_page_regions_dict["header"] = pseudo_region.text
        else:
            pseudo_page_regions_dict["text"].append(pseudo_region.text)

    # ---- INSERT IN GT-STRUCTURE-PAGE-XML -----
    pcgts = parse(gt_structure_path)
    page = pcgts.get_Page()
    # create list of all region types in gt-structure-page-xml
    region_types = list(set(region.get_type() for region in page.get_TextRegion()))
    # adjust as needed
    singular_text_region_types = ["page-number", "header"]
    page_xml_regions_dict = {
        region_type: None if region_type in singular_text_region_types else [] for region_type in region_types
    }

    for region in page.get_TextRegion():
        if region.get_type() in singular_text_region_types:
            page_xml_regions_dict[region.get_type()] = region
        else:
            page_xml_regions_dict[region.get_type()].append(region)

    if page_nb:
        page_xml_regions_dict["page-number"].replace_TextEquiv_at(0, TextEquivType(Unicode=page_nb))
    if pseudo_page_regions_dict["header"]:
        page_xml_regions_dict["header"].replace_TextEquiv_at(
            0, TextEquivType(Unicode=pseudo_page_regions_dict["header"])
        )

    # here we assume the i-th paragraph in the gt_structure-page-xml is also the i-th
    # path in the gt-text-pseudo-page-xml
    for i, paragraph in enumerate(page_xml_regions_dict["paragraph"]):
        paragraph.replace_TextEquiv_at(0, TextEquivType(Unicode=pseudo_page_regions_dict["text"][i]))

    with open(out_path, "w") as f:
        f.write(to_xml(pcgts))


merge(
    gt_structure_path="gt_structure_1_1/data/beck_eisen01_1884/GT-PAGE/beck_eisen01_1884_0027.xml",
    gt_text_path="gt_structure_1_1/data/beck_eisen01_1884/PSEUDO-PAGE/p27.xml",
    out_path="gt_structure_1_1/data/beck_eisen01_1884/OCR-D-MERGED/beck_eisen01_1884_0027.xml",
)
