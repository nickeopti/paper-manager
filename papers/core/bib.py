import subprocess
import tempfile

import lxml.etree

import papers.models

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
    authors_string = ', '.join(authors[:-1]) + ' & ' + authors[-1] if len(authors) > 1 else authors[0]
    return papers.models.Paper(reference=reference, title=title, date=date, authors=authors_string)


def _extract_name(name) -> str:
    family_elem = name.xpath('bltx:namepart[@type="family"]', namespaces={'bltx': BIBLATEXML_NAMESPACE})[0]
    nested_family = family_elem.xpath('bltx:namepart', namespaces={'bltx': BIBLATEXML_NAMESPACE})
    if nested_family:
        family = ' '.join(part.text for part in nested_family if part.text)
    else:
        family = family_elem.text

    given_elem = name.xpath('bltx:namepart[@type="given"]', namespaces={'bltx': BIBLATEXML_NAMESPACE})[0]
    nested_given = given_elem.xpath('bltx:namepart', namespaces={'bltx': BIBLATEXML_NAMESPACE})
    if nested_given:
        given = ' '.join(part.text for part in nested_given if part.text)
    else:
        given = given_elem.text

    prefix_elems = name.xpath('bltx:namepart[@type="prefix"]', namespaces={'bltx': BIBLATEXML_NAMESPACE})
    if prefix_elems:
        prefix_elem = prefix_elems[0]
        nested_prefix = prefix_elem.xpath('bltx:namepart', namespaces={'bltx': BIBLATEXML_NAMESPACE})
        if nested_prefix:
            prefix = ' '.join(part.text for part in nested_prefix if part.text)
        else:
            prefix = prefix_elem.text
        return f'{given} {prefix} {family}'
    else:
        return f'{given} {family}'
