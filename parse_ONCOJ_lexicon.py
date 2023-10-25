import sys, csv, re, os, xml.etree.ElementTree as ET
import pprint as pp
# from collections import namedtuple
from collections import defaultdict, Counter

ONCOJ_LEXICON_FILE='data/data-release/lexicon.xml'
ONCOJ_CORPUS_XML_DIR='data/data-release/xml'
ONCOJ_CORPUS_FILE='data/data-release/xml/MYS.1.5.xml'
POTENTIAL_WOSHIFT_LABIAL_XMLFILE='indeterminate_postlabial_wo_shifts.xml'
NON_INDETERMINATE_OUTFILE='OJ_lexicon_wo_shifted.csv'

OJ_WOSHIFT_PRELABIALS=set(['l','b'])
OJ_INDETERMINATE_WOSHIFT_POSTLABIALS=set('m')
OJ_VOWELS = re.compile(r'(wi|wo|ye|[aeiou])')

class IndeterminateWOShiftError(Exception):
    "indeterminate woshift"
    pass
                
def CVC_split(orth):
    if not orth: return ['']
    # split list will contain empty string if word does not begin or end
    # in a consonant
    return tuple(ph for ph in re.split(OJ_VOWELS,orth) if ph)

def is_disyllable(orth):
    cvc_split = CVC_split(orth)
    # first strip consonants from cvc_split
    if len(cvc_split) > 0 and not re.match(OJ_VOWELS,cvc_split[0]): cvc_split = cvc_split[1:]
    if len(cvc_split) > 0 and not re.match(OJ_VOWELS,cvc_split[-1]): cvc_split = cvc_split[:-1]
    return 2 <= len(cvc_split) <= 3

def woshift(orth):
    woshiftedOrth = []
    for idx,phoneme in enumerate(orth):
        precedent = orth[idx-1] if idx > 0 else None
        if precedent in OJ_INDETERMINATE_WOSHIFT_POSTLABIALS and orth[idx] == 'wo':
            raise IndeterminateWOShiftError
        elif precedent in OJ_WOSHIFT_PRELABIALS and orth[idx] == 'wo':
            woshiftedOrth.append('o')
        else: woshiftedOrth.append(orth[idx])
    return tuple(woshiftedOrth)

def parse_lexicon_file(oncoj_xml_file):
    woshiftedCounter = Counter()
    tree = xml.etree.ElementTree.parse(oncoj_xml_file)
    root = tree.getroot()
    namespace = root.tag.rstrip("div")
    entries = []
    for superEntry in root.findall(f"./{namespace}superEntry"):
        superEntryId=list(superEntry.attrib.values())[0]
        superEntryEntries = []
        for entry in superEntry.findall(f"./{namespace}entry"):
            orths = tuple(o.text for o in entry.findall(f"./{namespace}form/{namespace}orth"))
            defs = tuple(d.text for d in entry.findall(f"./{namespace}sense/{namespace}def"))
            pos = tuple(p.text for p in entry.findall(f"./{namespace}form/{namespace}gramGrp/{namespace}pos"))
            orths = tuple(CVC_split(o) for o in orths)
            superEntryEntries.append({'superid': superEntryId, 'orths': orths, 'defs': defs, 'pos': pos})
            
        # create woshift for this superEntry
        # if the is an indeterminate prelabial
        indeterminate_woshift = False
        try:
            for e in superEntryEntries:
                e['woshifted'] = tuple(woshift(o) for o in e['orths'])
                woshiftedCounter[e['woshifted']] += 1
            root.remove(superEntry) # we successfully processed this superEntry, remove it from the XML file
        except IndeterminateWOShiftError:
            # IndeterminateWOShift will remain in the XML file and we will print them out in POTENTIAL_WOSHIFT_LABIAL_XMLFILE at end
            continue
        entries += superEntryEntries
    tree.write(POTENTIAL_WOSHIFT_LABIAL_XMLFILE)
    for entry in entries: print(entry)
    print("\n", "unique words", len(woshiftedCounter))
    print("total words", woshiftedCounter.total())
    print(woshiftedCounter.most_common(15))
    # with open(csv_file, 'w', newline='') as csvfile:

def lemma_count(lemmaDD):
    # consolidates counts per lemma spelling across ujsages
    return {lm:c.total() for lm,c in lemmaDD.items()}

def compile_xml_lemma_counts(corpus_xml_dir):
    lemmas = defaultdict(dict)
    for corpus_xml in os.listdir(corpus_xml_dir):
        parse_xml_corpus_lemma_counts(lemmas, os.path.join(corpus_xml_dir, corpus_xml))
    return lemmas

def parse_xml_corpus_lemma_counts(lemmas, corpus_xml):
    tree = ET.parse(corpus_xml)
    root = tree.getroot()
    XMLlemmas = [w for w in root.findall(".//*[@lemma]")]
    XMLlemmas += [w for w in root.findall(".//w") if w not in XMLlemmas]  # try both w nodes and nodes with lemma attribute
    for w in XMLlemmas:
        if('lemma' in w.attrib):
            lemma, wtype = w.attrib['lemma'], w.attrib['type']
            texts = tuple(c.text for c in w.findall("./c"))
            if texts:
                if lemma not in lemmas: lemmas[lemma] = defaultdict(Counter)
                if len(texts) > 1:
                    # for multi-part lemmas, id by concatnatestring but save that we did this in the tyhpe info
                    wtype = (wtype,texts)
                    texts = ''.join(texts)
                else: texts = texts[0]
                lemmas[lemma][texts][wtype] += 1


if __name__ == "__main__":
    # with open(POTENTIAL_WOSHIFT_LABIAL_XMLFILE,'w') as pxml:
    # parse_lexicon_file(ONCOJ_LEXICON_FILE)
    # parse_xml_corpus_lemma_counts(ONCOJ_CORPUS_FILE)
    lemmas = compile_xml_lemma_counts(ONCOJ_CORPUS_XML_DIR)
    # pp.pprint(lemmas)
    print('lemma count:',len(lemmas))
    print('lemmas with unambiguous spelling:', sum(len(v) for v in lemmas.values() if len(v)==1))
    disyllables = {lm:lemma_count(dd) for lm,dd in lemmas.items() if all(is_disyllable(sp) for sp in dd.keys())}
    pp.pprint(disyllables)
    print('unambiguous disyllable count:', len(disyllables))
    # print(f"XML to CSV conversion completed. CSV file saved as {NON_INDETERMINATE_OUTFILE}")

  
