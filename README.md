# OJ_contigency
Statistical analysis of the co-occurence of vowels in Old Japanese from the Oxford NINJAL Corpus of Old Japanese.

Statistical Analysis
=============================================
OJ_disyllabic_correspondence_analysis_R.txt: 
   R commands for contingency analysis of vowels in disyllabic words.

Data files
=============================================
data/data-release/lexicon.xml
   ONCOJ XML lexicon of Old Japanese from https://oncoj.ninjal.ac.jp/
   
indeterminate_postlabial_wo_shifts.xml
   Subset of words in lexicon.xml with potential post-labial vowel shifts that require expert curation.

OJ_lexicon_wo_shifted.csv
   Collation of the ONCOJ lexicon file to be input into analysis in R.

Data pre-processing
=============================================
parse_ONCOJ_lexicon.py
   tokenizes the words in lexicon.xml into vowels and consonants and computes
   algorithmic vowel shifts. Outputs indeterminate_postlabial_wo_shifts.xml and 
   OJ_lexicon_wo_shifted.csv.
