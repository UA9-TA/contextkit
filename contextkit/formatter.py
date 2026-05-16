import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom


def format_bundle(bundle_items: dict[str, str], format_type: str = "markdown") -> str:
    """
    Format a bundle of files into the desired format.
    bundle_items maps file_path to content.
    """
    if format_type == "markdown":
        return _format_markdown(bundle_items)
    elif format_type == "xml":
        return _format_xml(bundle_items)
    elif format_type == "plain":
        return _format_plain(bundle_items)
    else:
        raise ValueError(f"Unknown format type: {format_type}")

def _format_markdown(bundle_items: dict[str, str]) -> str:
    out = []
    for path, content in bundle_items.items():
        ext = Path(path).suffix.lstrip(".")
        if not ext:
            ext = "text"

        out.append(f"## {path}\n")
        out.append(f"```{ext}")
        out.append(content)
        out.append("```\n")
    return "\n".join(out)

def _format_xml(bundle_items: dict[str, str]) -> str:
    root = ET.Element("context_bundle")
    for path, content in bundle_items.items():
        file_elem = ET.SubElement(root, "file", path=path)
        content_elem = ET.SubElement(file_elem, "content")
        content_elem.text = content

    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    # The [23:] slice is to remove the <?xml version="1.0" ?> header
    return reparsed.toprettyxml(indent="  ")[23:].strip()

def _format_plain(bundle_items: dict[str, str]) -> str:
    out = []
    for path, content in bundle_items.items():
        out.append(f"--- File: {path} ---")
        out.append(content)
        out.append("")
    return "\n".join(out)
