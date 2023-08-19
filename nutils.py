#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for File handling, regular expressions, and dictionary manipulation
"""

import os,re,sys,random,shutil,string,itertools,collections,stat,hashlib,csv
from pathlib import Path
# import time
IGNORABLE_SYSFILES = {'desktop.ini','thumbs.db','THUMBS.DB','Thumbs.db'}
DOTEXT_LIKE = re.compile(r'\.([^.]+)$')

# =======================================================================================================================================================================
# _______________________________  getargs()   ________________________________________________________________________
def grab2args(default1,default2=None):
   arg1 = sys.argv[1].strip('"').strip("'") if len(sys.argv) > 1 else default1
   arg2 = sys.argv[2].strip('"').strip("'") if len(sys.argv) > 2 else default2
   if isinstance(default1,int): arg1 = int(arg1)
   if isinstance(default2,int): arg2 = int(arg2)
   return arg1,arg2

# _______________________________   makedir()  ________________________________________________________________________
'''make a directory if it does not exist
   allows 1)specification of child_dir, or
          2)making a directory to house filenmae e.g.:
               makedir("C:/documents/foo/bar.txt") will make "C:/documents/foo/"
'''
def makedir(p_dir, child_dir=None):
   p_dir = Path(p_dir) /  ('.' if child_dir is None else child_dir)
   if re.search(DOTEXT_LIKE,p_dir.name): p_dir = p_dir.parent
   p_dir.mkdir(parents=True, exist_ok=True)
   return str(p_dir)

# _______________________________   splitpath()   _____________________________________________________________________
def splitpath(path, use_abspath=False, exclude_filename=True):
   path = os.path.abspath(str(path)) if use_abspath else str(path)
   pathsplit = os.path.normpath(path).split(os.sep)
   if exclude_filename and pathsplit and re.search(DOTEXT_LIKE,pathsplit[-1]): pathsplit = pathsplit[:-1]
   return pathsplit

# _______________________________   add_sufx()   ______________________________________________________________________
def splitext(fpath,force_split=False):
   head,ext = os.path.splitext(fpath)
   if ext=='' and force_split: head, ext = head[:-4], '.' +head[-3:]
   if len(ext) > 4:
      ext = (regex.match[0] if regex(r'(\.(?:jpeg|webm|html|docx|json|xlsx|docx|pptx|webp|class|java|download))',ext)
         else ext[:4])
   return head, ext



def split_filename(fpath,force_ext_split=False):
   dirpath,filebase = os.path.split(re.sub(r'["?*<>|]','',os.path.normpath(fpath)))
   return (dirpath,) +splitext(filebase,force_ext_split)

def add_sufx(fpath,suffix):
   return suffix.join(splitext(fpath))

# _______________________________  delete_foldertree()  _______________________________________________________________
def delete_foldertree(mydir):
   try: shutil.rmtree(mydir)
   except Exception as e: print(e)

# _______________________________  delete_dir_if_empty()   ____________________________________________________________
def delete_dir_if_empty(mydir):
   if not next(genwalk(mydir),False):
      delete_foldertree(mydir)

# _______________________________    read_csv()    ____________________________________________________________________
def read_csv(csvfile, to_dict=False):
   lines = []
   with open(csvfile, newline='', encoding='utf-8') as f:
      csvr = (csv.DictReader(f, delimiter=',', quotechar='"') if to_dict else
             csv.reader(f, delimiter=',', quotechar='"'))
      try:
         for row in csvr: lines.append(row)
      except UnicodeDecodeError as e:
         print('UnicodeDecodeError importing',csvfile,e)
         raise e
   return lines

# _______________________________  childdirs(), childfiles(), get_walkpaths(), get_walkfiles() ________________________
'''
   Non-recursive or recursive file/directory search
   Parameters:
      mydir: The directory to run on. os.getcwd() if None.
      filefilter: A filter-in on file basenames.
                  All files returned(no filtering) if filefilter is None or not given.
                  If a string, returns all files matching pattern;
                  Else (assumes function) returns filter(filefilter).
   Returns: list of abspaths of all matching files/directories

   Examples: childdirs("../foo"), get_walkfiles("./..", nmedia.is_image),
             childfiles("lib", r'.js$'), get_walkdirs(filefilter=r'^lib$')
'''
def childfiles(lsdir=None, filefilter=None):
   return _resolve_as_string(genls(lsdir,1,filefilter))

def childdirs(lsdir=None, filefilter=None):
   return _resolve_as_string(genls(lsdir,0,filefilter))

def get_walkfiles(walkdir=None, filefilter=None):
   return _resolve_as_string(genwalk(walkdir,1,filefilter))

def get_walkdirs(walkdir=None, filefilter=None):
   return _resolve_as_string(genwalk(walkdir,0,filefilter))

# (files or dirs) ls-paths of scandir relative to current dir
def genls(lsdir=None,files=True, namefilter=None):
   return _basename_filter(namefilter, (p for p in Path('.' if lsdir is None else lsdir).iterdir() 
      if ((p.is_file() and p.name not in IGNORABLE_SYSFILES) if files else p.is_dir())))

# (files or dirs) walk-paths of scandir relative to current dir
def genwalk(walkdir=None,files=True, namefilter=None):
   return _basename_filter(namefilter, (p for p in Path('.' if walkdir is None else walkdir).glob('**/*' if files else '**') 
      if ((p.is_file() and p.name not in IGNORABLE_SYSFILES) if files else True)))

def _basename_filter(filefilter,pathgen):
   if filefilter is None: return pathgen
   filter_f = (filefilter if not isinstance(filefilter,str) else
               (lambda p: re.search(filefilter,p)))
   return (p for p in pathgen if filter_f(p.name))

def _resolve_as_string(pathgen):
   return [str(p.resolve()) for p in pathgen]

# _______________________________  randsuffix_filename() ______________________________________________________________
def randsuffix_filename(path):
   randsuffix = '-' +''.join(random.choice('123456789ABCDEFGHHIJKLMNOPQRSTUVWXYZ') for _ in range(6))
   return add_sufx(path,randsuffix)

'''@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@____________________________   Sequence Functions     ______________________________________________________________________________________________________________@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@_________________________@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'''


# _______________________________   flatten()   _______________________________________________________________________
''' Unlike itertools.chain, wont decompose str,bytes '''
def flatten(nested_seq):
   if not isinstance(nested_seq, (str, bytes)):
      if isinstance(nested_seq,dict): nested_seq = nested_seq.items()
      try: return list(_flatten_g(iter(nested_seq)))
      except TypeError: pass
   return nested_seq

def _flatten_g(l):
   for el in l:
      if isinstance(el, (str, bytes)): yield el
      elif isinstance(el, dict): yield from _flatten_g(itertools.chain(el.items()))
      else:
         try: yield from _flatten_g(iter(el))
         except TypeError: yield el

# _______________________________    wAlts()    _______________________________________________________________________
def wAlts(mutate_f,seq):
   if isinstance(seq, set): return seq | {mutate_f(s) for s in seq}
   return seq + [mutate_f(s) for s in seq]

# _______________________________   nfirst(),nfirstIdx()     __________________________________________________________
''' first() with memory side effect and predicate filter
      Remember filter returns values for which pred(item) is True, or all items if pred is None
'''
def nfirst(seq,pred=None):
   nfirst.next = next(filter(pred, seq), None)
   return nfirst.next
def nfirstIdx(seq,pred):
   nfirstIdx.i = next(i for i,x in enumerate(seq) if pred(x))
   return nfirstIdx.i
# def match(seq,item,pred=None): return next((x for x in seq if (x if pred is None else pred(x)) == item), None)
# def matchIdx(seq,el): return next((i for i,x in enumerate(seq) if x==el), None)

# _______________________________    duplicates()    __________________________________________________________________
def get_duplicates(seq,pred=None):
   c = collections.Counter(seq if pred is None else (pred(x) for x in seq))
   return [x for x in seq if c[x] > 1], c

# _______________________________   multi_re_sub()   __________________________________________________________________
# e.g.
# NUMBER_REPLACEMENTS = {
   # r' NO(\d*)?\W*$' : r' Number \1',
   # r'\b(?:number|no) ?(\d\d?)\b' : r'Number \1',
   # r'([a-zA-Z]+)(\d+)\b' : r'\1 \2',
   # r'([a-zA-Z]+) ?(10|[1-9])([a-zA-Z])\b' : r'\1 \2\3'
# }
# multi_re_sub(mystr,NUMBER_REPLACEMENTS)

def multi_re_sub(mystr, resub_d):
   for pattern,replacement in resub_d.items():
      mystr = re.sub(pattern, replacement, mystr, flags=re.IGNORECASE)
   return mystr

# For compiled patterns, assumes any flags are already compiled
def multi_recomp_sub(mystr, resub_d):
   for pattern,replacement in resub_d.items():
      mystr = re.sub(pattern, replacement, mystr)
   return mystr

# _______________________________   remove punctuation()   ____________________________________________________________
# This uses the 3-argument version of str.maketrans with arguments (x, y, z) where 'x' and 'y'
# must be equal-length strings and characters in 'x' are replaced by characters in 'y'.
# 'z' is a string (string.punctuation here) where each character in the string is mapped to None

# REMOVE_PUNCTUATION_TRANSLATOR = str.maketrans('', '', string.punctuation)
# REMOVE_PUNCTUATION_UNDERSCORE_EXCEPT_UNDERSCORE = str.maketrans('', '', string.punctuation.replace('_',''))
# REMOVE_PUNCTUATION_UNDERSCORE_TO_SPACE_TRANSLATOR = str.maketrans('_', ' ', string.punctuation.replace('_',''))
#
# def unpuctuate(punctuated_str):
   # return punctuated_str.translate(REMOVE_PUNCTUATION_TRANSLATOR)
#
# def unpuctuate_except_underscore(punctuated_str):
   # return punctuated_str.translate(REMOVE_PUNCTUATION_UNDERSCORE_EXCEPT_UNDERSCORE)
   #
# def unpuctuate_underscore_to_space(punctuated_str):
   # return punctuated_str.translate(REMOVE_PUNCTUATION_UNDERSCORE_TO_SPACE_TRANSLATOR)

# _______________________________    strip_emptystrs    _______________________________________________________________
def strip_emptystrs(mystrs):
   return [s for s in [s.strip() for s in mystrs] if s]

# _______________________________    strip_emptystrs    _______________________________________________________________
def linesplit(mystr):
   return strip_emptystrs(re.split(r'(\r?\n|</?(?:p|br|h\d|li|ul)(?:\s[^>]*)?>)',mystr))

# _______________________________   extract_values_nested()   _________________________________________________________
def get_values_nested(key, nested_dict_or_list):
   return list(_gen_dict_extract_r(key,nested_dict_or_list))

def _gen_dict_extract_r(key, var):
   if hasattr(var,'items'):
      for k, v in var.items():
         if k == key:
            yield v
         if isinstance(v, dict):
            for result in _gen_dict_extract_r(key, v):
               yield result
         elif isinstance(v, list):
            for d in v:
               for result in _gen_dict_extract_r(key, d):
                  yield result
   elif isinstance(var, list):
      for d in var:
         for result in _gen_dict_extract_r(key, d):
            yield result

# _______________________________    sha1_file()    ___________________________________________________________________
def sha2_file(fpath):
   hasher, BLOCKSIZE = hashlib.sha512(), 128*1024
   with open(fpath, 'rb') as f:
       buf = f.read(BLOCKSIZE)
       while len(buf) > 0:
           hasher.update(buf)
           buf = f.read(BLOCKSIZE)
   return hasher.hexdigest()

# _______________________________   winMoveFile     ___________________________________________________________________
'''Enforces file movement A)across directories B) for read-only files.
   May throw errors (?) which should still be checked'''
def winMoveFile(src,dst,remove_duplicate_src=False):
   try:
      shutil.move(src,dst,copy_function=copyreadonly)
   except IOError as e:
      dst_file = os.path.join(dst,os.path.basename(src))
      if (remove_duplicate_src and
          re.search(r'already exists',str(e)) and
          sha2_file(src) == sha2_file(dst_file)):
         print(str(e) +'. Deleting sha2-identical file', src)
         os.unlink(src)
      else: raise e
   if os.path.isfile(dst) and os.path.isfile(src):
      os.unlink(src)
   return dst
def copyreadonly(src, dst):
   os.chmod(src, stat.S_IWRITE)
   shutil.copy2(src,dst)

# _______________________________   legitimize_windows_filestring     _________________________________________________
def legitimize_windows_filestring(filestr):
   # filestr = filestr.encode('ascii','ignore')
   head, ext = os.path.splitext(filestr)
   return re.sub('"',"'", re.sub(r'[/\\:>|*\n\r\t?\][<+-]', '', head))[:100].strip() +ext

# _______________________________    canonize_punctcaps    ____________________________________________________________
PUNCTUATION_REMOVER = str.maketrans('','',string.punctuation)
def canonize_punctcaps(mystring):
   return ' '.join(mystring.translate(PUNCTUATION_REMOVER).lower().split())

# _______________________________   regex()  __________________________________________________________________________
'''
@@@@@  Convenience regex that retains match as a Perl-style side effect in function variable
@@@@@  Motivation behind regex() is to allow classic, concise, Perl-style usage e.g.:
@@@@@     "if regex(pat,str): foo += regex.match[0]"
@@@@@  By using regex() smartly, you can replace many of the clunky, verbose mechanics in the Python re module.
RETURN VALUE:  ()                          #python_REGX did not match target_string, (return empty tuple).
     --        (re.search(),)            #python_REGX did match, but any subgroups for python_REGX were all empty.
     --        re.search().groups()        #python_REGX matched and found nonempty subgroups!!
     --        re.search().groups()[0]     #If PARAMETER first_match_only=True.
SIDE EFFECT:   regex.match==(RETURN VALUE), is a FUNCTION VAIABLE bound to regex() itself. regex.match will persist in
               the name-space, so it's matches can be used by any code. A regex() call subsequent in execution will
               reset regex.match => so take advantage before then!
'''

def regex(python_REGX, target_string, flags=re.IGNORECASE):
   regex.match, mobj = (), re.search(python_REGX,target_string, flags)
   if mobj:
      # nonempty_subgroups = [g for g in mobj.groups() if g]
      # regex.mobj = mobj
      # regex.match = mobj.groups()[:first_match_only or None] if mgroups else (target_string,)
      regex.mobj = mobj
      # groups() are subgroups (if those were provided in pattern), group() is non-subgroup pattern
      regex.match = mobj.groups() or mobj.group()
      regex.pre = target_string[:mobj.start()]
      regex.post = target_string[mobj.end():]
   return regex.match


# _______________________________   multimap()   ______________________________________________________________________
# e.g.   nutils.multimap([(int(i/2),i) for i in range(10)])
#        nutils.multimap(range(10), func=lambda x: int(x/2))
def multimap(seq, vToSet=False,vSort=False,vSortKey=None, pred=None):
   mm = collections.defaultdict(list)
   if pred is None:
      for k,v in seq: mm[k].append(v)
   else:
      for x in seq: mm[pred(x)].append(x)

   if vToSet:
      for k in mm.keys():
         mm[k] = set((tuple(v) if isinstance(v,list) else v) for v in mm[k])
   elif vSort or (vSortKey is not None):
      for k in mm.keys():
         mm[k] = sorted(mm[k], key=vSortKey)
   return mm

# For pretty printing, etc.
def mm_deconstruct(mm):
   def mmseq_deconstruct(mms):
      if len(mms) > 1: return [list(v) for v in mms]
      mms = list(mms)[0]
      if isinstance(mms,tuple) or isinstance(mms,list): return mms[0] if len(mms)==1 else list(mms)
      return mms
   return {k:mmseq_deconstruct(mmseq) for k,mmseq in mm.items()}

# Ssorted first by list length, then key
# e.g.   nutils.sorted_mm_byfreq([(int(i % 3),i) for i in range(10)])
def sorted_mm_byfreq(mmseq, key=None):
   if hasattr(mmseq,'items'):
      if key is not None:
         return sorted(mmseq.items(), key=lambda t: (-len(t[1]),key(t[0])) )
      return sorted(mmseq.items(), key=lambda t: (-len(t[1]),t[0]) )
   return sorted_mm_byfreq(multimap(mmseq), key=key)

# _______________________________   to_freqtable()   ___________________________________________________________________
# nutils.to_freqtable([int(i % 6) for i in range(10)])
#   '(n=2,0), (n=2,1), (n=2,2), (n=2,3), (n=1,4), (n=1,5)'
#  nutils.to_freqtable([int(i % 6) for i in range(10)], tostring=False)
#   [(2, 0), (2, 1), (2, 2), (2, 3), (1, 4), (1, 5)]
# nutils.to_freqtable([int(i % 8) for i in range(10)])  #merging insufficient to meet mergeAt_fraction]
#   '0, 0, 1, 1, 2, 3, 4, 5, 6, 7'
# nutils.to_freqtable([int(i % 8) for i in range(10)],mergeAt_fraction=0.9)
#   (n=2,0), (n=2,1), (n=1,2), (n=1,3), (n=1,4), (n=1,5), (n=1,6), (n=1,7)
def to_freqtable(mylist, tostring=True, mergeAt_fraction=0.7, joinstr=', ',):
   if tostring and (mergeAt_fraction * len(mylist) < len(set(mylist))):
      return joinstr.join(str(x) for x in sorted(mylist))
   freqtable = sorted(collections.Counter(mylist).most_common(), key=lambda t:(-t[1],t[0]))
   return (joinstr.join('(n='+str(n)+','+str(x) +')' for x,n in freqtable) if tostring else
          [(n,x) for x,n in freqtable])

# print ex1 <-(src1,src2,src3)
#       ex1 <-(src1,src2,src3)
#       ex1 <-(src1,src2,src3)
#       ex1 <-(src1,src2,src3)
def concat_fields(mm_byfreq, text_cutoff=40):
   fields_grouped = [ (str(field).replace('"',''), to_freqtable(progs)) for field,progs in mm_byfreq]
   return '\n'.join( field[:text_cutoff] +' <- (' +progs +')' for field,progs in fields_grouped )


# _______________________________    profiling    ______________________________________________________________________
# #First, create profile with: python -m cProfile -o stats.cprof condition_parse.py
def profile_stats(head=60):
   import pstats
   p = pstats.Stats('stats.cprof')
   # python 3.6
   # p.strip_dirs().sort_stats('cumulative').print_stats(int(head*.66))  # sort by time spent in function (including subfunctions)
   # p.strip_dirs().sort_stats('time').print_stats(head)                 # sort by time spent in function (not subfunctions)
   # python 3.7
   p.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(head)  #sort by time spent in function (not subfunctions)
   p.sort_stats(pstats.SortKey.TIME).print_stats(head)        #sort by time spent in function (not subfunctions)


