import sys, csv, re, os, math, csv, xml.etree.ElementTree as ET
import pprint as pp
import matplotlib.pyplot as plt
# from collections import namedtuple
from collections import defaultdict, Counter

ONCOJ_LEXICON_FILE='data/data-release/lexicon.xml'
ONCOJ_CORPUS_XML_DIR='data/data-release/xml'
ONCOJ_CORPUS_FILE='data/data-release/xml/MYS.1.5.xml'
POTENTIAL_WOSHIFT_LABIAL_XMLFILE='indeterminate_postlabial_wo_shifts.xml'
NON_INDETERMINATE_OUTFILE='OJ_lexicon_wo_shifted.csv'

OJ_WOSHIFT_PRELABIALS=set(['l','b'])
OJ_INDETERMINATE_WOSHIFT_POSTLABIALS=set('m')
OJ_VOWELS = set(['wi','wo','ye','a','e','i','o','u'])
OJ_VOWELS_R = re.compile(r'(wi|wo|ye|[aeiou])')

class IndeterminateWOShiftError(Exception):
    "indeterminate woshift"
    pass
                
def CVC_split(orth):
    if not orth: return ['']
    # split list will contain empty string if word does not begin or end in a consonant
    return tuple(ph for ph in re.split(OJ_VOWELS_R,orth) if ph)

def n_syllables(orth):
    return len([ph for ph in CVC_split(orth) if ph in OJ_VOWELS])

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


def lemma_count(lemmaDD):
    # consolidates counts per lemma spelling across ujsages
    return {lm:c.total() for lm,c in lemmaDD.items()}

def collapse_lemma_usage_counts(lemmas):
    return {lm:lemma_count(lmdd) for lm,lmdd in lemmas.items() }

def lemma_n_syllables(lemma):
    return max(n_syllables(orth) for orth in lemma.keys())

def lemma_is_spelled_unambiguously(lemma):
    return len(lemma) == 1

def total_variation_from_unif(count):
    N, M = len(count), count.total()
    return sum(abs(x/M - 1/N) for _,x in count.most_common()) * 0.5  # *N/(N-1)

def KL_distance(count):
    N, M = len(count), count.total()
    return sum(x*math.log2(x*N/M)/M for _,x in count.most_common()) / math.log2(N)

def plot_frequency_imbalance(lemmas,plot_title,savefile):
    #create histogram of l1 divergence from uniform distribution in the ambiguous lemmas
    divs = [total_variation_from_unif(Counter(dd)) for dd in lemmas.values() if not lemma_is_spelled_unambiguously(dd)]
    print('proportion of counts more unbalanced than 5:1',sum(1 for d in divs if d > 1/3)/len(divs))
    print('proportion of counts more unbalanced than 10:1',sum(1 for d in divs if d > 0.40909)/len(divs))
    plt.hist(divs, range=(0,1), bins=150)
    plt.title(plot_title)
    plt.xlabel("total variation")
    plt.savefig(savefile)
    plt.show()

def print_lemma_stats(lemmas):
    # print lemma counts
    print('lemma count:',len(lemmas))
    print('lemmas with unambiguous spelling:', sum(1 for dd in lemmas_collapsed.values() if lemma_is_spelled_unambiguously(dd)))
    print('unique lemma counts by syllable length:',
          sorted(Counter([lemma_n_syllables(dd) for dd in lemmas.values()]).most_common()))
    print('unambiguous lemma counts by syllable length:',
          sorted(Counter([lemma_n_syllables(dd) for dd in lemmas.values() if lemma_is_spelled_unambiguously(dd)]).most_common()))

    # print lemma occurence counts in the corpus
    occurence_by_length = Counter()
    for dd in lemmas.values():
        if lemma_n_syllables(dd) == 0 : print('zero syllable lemma',dd)
        occurence_by_length[lemma_n_syllables(dd)] += sum(dd.values())
    print('lemma occurences by syllable length:', sorted(occurence_by_length.most_common()))
    unambiguous_occurence_by_length = Counter()
    for dd in lemmas.values():
        if lemma_is_spelled_unambiguously(dd):
            unambiguous_occurence_by_length[lemma_n_syllables(dd)] += sum(dd.values())
    print('unambiguous lemma occurences by syllable length:', sorted(unambiguous_occurence_by_length.most_common()))

    # pl/ot_frequency_imbalance(lemmas,
                             # 'Frequency Imbalance of Lemma Variants\n Histogram - Total Variation from Uniform Frequency',
                             # 'charts/variant frequency total variation histogram.png')
    # plot_frequency_imbalance({lm:dd for lm,dd in lemmas.items() if lemma_n_syllables(dd) ==2},
                             # 'Frequency Imbalance of Disyllable Variants\n Histogram - Total Variation from Uniform Frequency',
                             # 'charts/disyllable variant frequency total variation histogram.png')

def write_lemma_counts_csv(lemmas,savefile):
    with open(savefile, 'w', newline='') as csvfile:
        csvwr = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        csvwr.writerow(['idx','disyllable','id','V1','V2','count'])
        for idx,(lm,dd) in enumerate(lemmas.items()):
            if lemma_is_spelled_unambiguously(dd):
                orth,count = list(dd.items())[0]
                v1,v2 = [ph for ph in CVC_split(orth) if ph in OJ_VOWELS][:2]
                csvwr.writerow([idx,orth,lm] + [v1,v2] + [count])


if __name__ == "__main__":
    # parse_lexicon_file(ONCOJ_LEXICON_FILE)
    # parse_xml_corpus_lemma_counts(ONCOJ_CORPUS_FILE)
    lemmas = compile_xml_lemma_counts(ONCOJ_CORPUS_XML_DIR)
    lemmas_collapsed = collapse_lemma_usage_counts(lemmas)
    disyllables = {lm:dd for lm,dd in lemmas_collapsed.items() if lemma_n_syllables(dd) ==2}
    pp.pprint(disyllables)
    print_lemma_stats(lemmas_collapsed)
    write_lemma_counts_csv(disyllables,'data/ONCOJ XML lemmatized disyllables.csv')
    # print(f"XML to CSV conversion completed. CSV file saved as {NON_INDETERMINATE_OUTFILE}")

  
