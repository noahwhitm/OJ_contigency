import sys, csv, re, xml.etree.ElementTree

ONCOJ_LEXICON_FILE='data/data-release/lexicon.xml'
POTENTIAL_WOSHIFT_LABIAL_XMLFILE='indeterminate_labial_woshifts.xml'
NON_INDETERMINATE_OUTFILE='OJ_lexicon_woshifted.csv'

OJ_WOSHIFT_PRELABIALS=set(['l','b'])
OJ_INDETERMINATE_WOSHIFT_PRELABIALS=set('m')
OJ_VOWELS = re.compile(r'(wi|wo|ye|[aeiou])')

class IndeterminateWOShiftError(Exception):
    "indeterminate woshift"
    pass
                
def CVCSplit(orth):
    if not orth: return ['']
    # split list will contain empty string if word does not begin or end
    # in a consonant
    return re.split(OJ_VOWELS,orth)
    
def woshift(orth):
    woshiftedOrth = []
    for idx,phoneme in enumerate(orth):
        precedent = orth[idx-1] if idx > 0 else None
        if precedent in OJ_INDETERMINATE_WOSHIFT_PRELABIALS and orth[idx] == 'wo':
            raise IndeterminateWOShiftError
        elif precedent in OJ_WOSHIFT_PRELABIALS and orth[idx] == 'wo':
            woshiftedOrth.append('o')
        else: woshiftedOrth.append(orth[idx])
    return woshiftedOrth

def parse_lexicon_file(oncoj_xml_file):
    tree = xml.etree.ElementTree.parse(oncoj_xml_file)
    root = tree.getroot()
    namespace = root.tag.rstrip("div")
    entries = []
    for superEntry in root.findall(f"./{namespace}superEntry"):
        superEntryId=list(superEntry.attrib.values())[0]
        superEntryEntries = []
        for entry in superEntry.findall(f"./{namespace}entry"):
            orths = [o.text for o in entry.findall(f"./{namespace}form/{namespace}orth")]
            defs = [d.text for d in entry.findall(f"./{namespace}sense/{namespace}def")]
            pos = [p.text for p in entry.findall(f"./{namespace}form/{namespace}gramGrp/{namespace}pos")]
            orths = [CVCSplit(o) for o in orths] 
            superEntryEntries.append({'superid': superEntryId, 'orths': orths, 'defs': defs, 'pos': pos})
            
        # create woshift for this superEntry
        # if the is an indeterminate prelabial
        indeterminate_woshift = False
        try:
            for e in superEntryEntries:
                e['woshifted'] = [woshift(o) for o in e['orths']]
            root.remove(superEntry) # we successfully processed this superEntry, remove it from the XML file
        except IndeterminateWOShiftError:
            # IndeterminateWOShift will remain in the XML file and we will print them out in POTENTIAL_WOSHIFT_LABIAL_XMLFILE at end
            continue
        entries += superEntryEntries
    tree.write(POTENTIAL_WOSHIFT_LABIAL_XMLFILE)
    # for entry in entries: print(entry)
    # with open(csv_file, 'w', newline='') as csvfile:
    


if __name__ == "__main__":
    # with open(POTENTIAL_WOSHIFT_LABIAL_XMLFILE,'w') as pxml:
    parse_lexicon_file(ONCOJ_LEXICON_FILE)
    print(f"XML to CSV conversion completed. CSV file saved as {NON_INDETERMINATE_OUTFILE}")

  