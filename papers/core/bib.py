import dataclasses
import subprocess
import tempfile

import lxml.etree


@dataclasses.dataclass
class Paper:
    reference: str
    title: str
    date: str
    authors: list[str]


BIBLATEXML_NAMESPACE = 'http://biblatex-biber.sourceforge.net/biblatexml'


class BiberError(RuntimeError):
    pass


def parse_bib_file(file_path: str):
    with tempfile.NamedTemporaryFile(suffix='.bltxml') as temp_file:
        result = subprocess.run(
            ['biber', '--tool', '--output-format=biblatexml', '--output-file', temp_file.name, file_path],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise BiberError(f'Failed to parse BibTeX file: {result.stderr}')

        with open(temp_file.name, 'r', encoding='utf-8') as file:
            tree = lxml.etree.parse(file, parser=lxml.etree.XMLParser())

    entry = tree.xpath('//bltx:entry[1]', namespaces={'bltx': BIBLATEXML_NAMESPACE})[0]
    reference = entry.get('id')
    title = entry.xpath('bltx:title', namespaces={'bltx': BIBLATEXML_NAMESPACE})[0].text
    date = entry.xpath('bltx:date', namespaces={'bltx': BIBLATEXML_NAMESPACE})[0].text
    authors = [
        _extract_name(name)
        for name in entry.xpath('bltx:names[@type="author"]/bltx:name', namespaces={'bltx': BIBLATEXML_NAMESPACE})
    ]
    return Paper(reference=reference, title=title, date=date, authors=authors)


def _extract_name(name) -> str:
    family_elem = name.xpath('bltx:namepart[@type="family"]', namespaces={'bltx': BIBLATEXML_NAMESPACE})[0]
    family = family_elem.text

    given_elem = name.xpath('bltx:namepart[@type="given"]', namespaces={'bltx': BIBLATEXML_NAMESPACE})[0]
    nested_given = given_elem.xpath('bltx:namepart', namespaces={'bltx': BIBLATEXML_NAMESPACE})
    if nested_given:
        given = ' '.join(part.text for part in nested_given if part.text)
    else:
        given = given_elem.text
    return f'{given} {family}'
