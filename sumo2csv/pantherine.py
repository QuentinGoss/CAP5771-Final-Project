# pantherine.py
# Author: Quentin Goss
# My personal collection of python methods that I frequently use

import operator  # sortclasses, sortdicts
import pickle    # load, save
import os        # lsdir
import itertools # lncount
import glob      # mrf
import json      # save
import xml.etree.ElementTree as ET # readXML
from bisect import bisect_left     # binsearch
import datetime

# Converts a string of characters into a unique number
# @param string s = string of ASCII values
# @return int = a numerical representation of s
def ascii2int(s):
    return int(''.join(str(ord(c)) for c in s))

# Binary search
# @param [int] lst = Sorted list of integers to Look through
# @param int el = Element to find in the list
# @return int = index of item in the list or Value Error if not found
def binsearch(lst,el):
    # Locate the leftmost value exactly equal to x
    i = bisect_left(lst,el)
    if i != len(lst) and lst[i] == el:
        return i
    raise ValueError

# Binary search - Retrieves a range of indexes that match
# @param [int] lst = Sorted list of integers to Look through
# @param int el = Element to find in the list
# @return (low,high) = low and high indices of item in the list
#                      or Value Error if not found
def binrangesearch(lst,el):
    # Returns index if found, ValueError otherwise
    index = binsearch(lst,el)
    
    # Get the lower bound
    low = index
    while (not low-1 < 0) and (lst[low-1] == el):
        low -= 1
        
    # Get the uppper bound
    high = index
    while (not high+1 == len(lst)-1):
        try:
            if not lst[high+1] == el:
                break
        except IndexError:
            break
        high += 1
        
    return (low,high)

# Reads an XML file
# @param string _file = filename
# @return root = XML root
def readXML(_file):
    tree = ET.parse(_file)
    return tree.getroot()

# Reads a specified tag from an XML file
# @param string _file = filename
# @param string tag = name of XML tag
# @return [dict] = a list of dictionaries containing each tag that
#  matches tag
def readXMLtag(_file,tag):
    root = readXML(_file)
    return [item.attrib for item in root.findall(tag)]

# Checks if a given xml object has an attribute
# For use with import xml.etree.ElementTree as ET
# @param ElementTree-xml-object xml = xml tag
# @param string attrib =  attribute to check the existence of
# @return True if exists, False otherwise
def xml_has_atrribute(xml,attrib):
    try:
        len(xml.attrib[attrib])
        return True
    except:
        pass
    return False

# Prints out the current % progress
# @param int n = Current progress
# @param int total = the highest progress achievable
# @param str msg = Msg if any to be added to the update text
def update(n,total,msg=''):
    print('%s%6.2f%%' % (msg,float(n)/float(total)*100),end='\r')
    return

# Sort a list of classes by an attribute. Use this for sorting classes
# @param [classes] lst = list to be sorted
# @param string attr = atrribute name to be used in the sort.
# @param bool reverse = Reverse the order of the sorted list
# @return [] = sorted list
def sortclasses(lst,attr,reverse=False):
    return lst.sort(key=operator.attrgetter(attr),reverse=reverse)

# Sort a list of dictionaries by key
# @param [dict] lst = list to be sorted
# @param string key = key to be sorted by
# @param bool reverse = Reverse the order of the sorted list
# @return [] = sorted list
def sortdicts(lst,key,reverse=False):
    return sorted(lst,key=operator.itemgetter(key),reverse=reverse)

# Filters a list of dictionaries given a value and key
# @param [dict] lst = list to be sorted
# @param string key = key to be sorted by
# @param string or int val = Value to filter by
# @param bool no_sort = If False, skip the quantification and sorting
# @param bool invert = If True, return everything but the filtered items
# @return [dict] = A list of dictionaries that match the filter
def filterdicts(lst,key,val,no_sort=False,invert=False):
    # Validate Input
    if not objname(val) in {'int','str','float'}:
        raise TypeError
    if no_sort:
        try:
            type(lst[0]['sortID'])
        except:
            raise KeyError
        
    # Cast the value accordingly
    if not objname(val) in {'int','float'}:
        val = ascii2int(val)
    
    # Quantify Sort and serach
    if not no_sort:
        lst = quantifydicts(lst,key)
    sortIDs = [d['sortID'] for d in lst]
    low,high = binrangesearch(sortIDs,val)
    
    # Invert
    if invert:
        if low == high:
            if high == 0:
                return lst[1:]
            elif high == len(lst)-1:
                return lst[:-1]
            else:
                before = lst[:high]
                after = lst[high+1:]
                before.extend(after)
                return before
        else:
            if low == 0:
                before = []
            else:
                before = lst[:low]
            if high == len(lst)-1:
                after = []
            else:
                after = lst[high+1:]
            before.extend(after)
            return before
    
    # Return
    if low == high:
        return [lst[high]]
    else:
        return lst[low:high+1]

# <!> UNFINISHED <!>
# Performs filterdicts on a list of similiar values
# @param [dict] lst = list to be sorted
# @param string key = key to be sorted by
# @param [string or int] vals = List of value to filter by
# @param bool no_sort = If False, skip the quantification and sorting
# @param bool show_progress = If True, show progress %
# @return [[dict]] = A list of of lists of dictionaries that match the
#  input values
def batchfilterdicts(lst,key,vals,no_sort=False,show_progress=False):
    # Validate
    if not objname(vals) in {'list','tuple','set'}:
        raise TypeError
    
    if not no_sort:
        lst = quantifydicts(lst,key)
    # Look for the first item
    try:
        filtered = [filterdicts(lst,key,vals[0],no_sort=True)]
    except ValueError:
        filtered = [None]
    
    # If there is 1 item in the list, then return here
    if len(lst) == 1:
        return filtered
    
    # Try the rest of the items
    n = 1; total = len(vals)
    for val in vals[1:]:
        try:
            filtered.append(filterdicts(lst,key,val,no_sort=True))
        except ValueError:
            filtered.append(None)
        if show_progress:
            n += 1; update(n,total,msg="Batch filtering dicts ")
        continue
    
    return filtered

# Quantifies and sorts a list of dictionaries so they may be used in a binary search
# @param [dict] lst = list to be sorted
# @param string key = key to be sorted by
# @return [dict] with a new key ['sortID']
def quantifydicts(lst,key):
    for i in range(len(lst)):
        if objname(lst[i][key]) in {'int','float'}:
            lst[i]['sortID'] = lst[i][key]
        else:
            lst[i]['sortID'] = ascii2int(lst[i][key])
    return sortdicts(lst,'sortID')

# Save binary data to a file.
# - If .json is in the _file, then it saves in json format
# @param string _file = filename
# @param data = blob of data to be saved
def save(_file,data):
    if _file[-5:] == '.json':
        with open(_file,'w') as f:
            json.dump(data,f)
        return
    with open(_file,'wb') as f:
        pickle.dump(data,f)
    return

# Load binary data from a file
# <!> Must know what the data looks like to receive it. <!>
# @param string _file = filename
# @return = Blob of data from the file.
def load(_file):
    with open(_file,'rb') as f:
        return pickle.load(f)

# Get the number of lines in a file
# @param _file = filename
# @return int = number of lines in the file
def lncount(_file):
    with open(_file, 'rb') as f:
        bufgen = itertools.takewhile(lambda x: x, (f.raw.read(1024*1024) for _ in itertools.repeat(None)))
        return sum( buf.count(b'\n') for buf in bufgen )
        
# Returns the class name of an object
# @param obj = object to get name of
# @return str name = name of the object
def objname(obj):
    return type(obj).__name__

# Reads a .json file.
# @param string _file = filename
# @return dict = data as a dictionary
def readJSON(_file):
    with open(_file,'r') as f:
        return json.load(f)

# Reads a csv file. Creates a list of dictionaries from the contents
#  using the first line the keys
# @param string _file = filename
# @param bool guess_type = If true, guess what type the data is
# @return [dict] = A list of dictionaries 
def readCSV(_file,guess_type=False):
    with open(_file,'r') as f:
        ln = 0; keys = []; lst = []
        for line in f:
            ln += 1
            
            # Parse data from the line
            data = line.strip().split(',')
            
            # The first line holds the keys of the dictionary objects
            if ln == 1:
                keys = data
                continue
            
            # Guess the type if true
            if guess_type:
                for i in range(len(data)):
                    # float
                    if '.' in data[i]:
                        try: data[i] = float(data[i])
                        except ValueError: pass
                    # int
                    else:
                        try: data[i] = int(data[i])
                        except ValueError: pass
                    # Otherwise it's a str
                    continue
            
            # If the data continues past the last line,
            #  combine it in the last item
            nkeys = len(keys)
            if len(data) > nkeys:
                data[nkeys-1] = data[nkeys-1:]
                data = data[:nkeys]
            
            # Create the dictionary object and add to a list
            lst.append(list2dict(keys,data))
            continue
        #
    return lst

# Combine two lists to create a dictionary
# @param [str] = List is keys
# @param [] = List of values 
def list2dict(keys,vals):
    return dict(zip(keys,vals))

# Casts every object in the list to specified type
# @param [str or int or float] lst = list of any type of values
#   or if the item is not a list, then it is simply cast and returned.
# @param string _type = What the values in the list should be cast to
# @return [] = A list where the objects are cast to the specified type
def castlist(lst,_type):
    # If the object is a list
    if objname(lst) in {'list','tuple','set'}:
        if _type.lower() in {'str','string'}:
            return [str(item) for item in lst]
        elif _type.lower() in {'int','integer'}:
            return [int(item) for item in lst]
        elif _type.lower() in {'float'}:
            return [float(item) for item in lst]
    
    # If the object is a str, float, or int
    elif objname(lst) in {'str','float','int'}:
        if _type.lower() in {'str','string'}:
            return str(lst)
        elif _type.lower() in {'int','integer'}:
            return int(lst)
        elif _type.lower() in {'float'}:
            return float(lst)
    raise ValueError

# Casts the values of all the dictionaries in the list that correspond
#   to the given key
# @param [dict] lst = list if dictionaries that will be manipulated
# @param string key = key that will be casted
# @param string _type = type to be casted to
# @return [dict] = A list of dictionaries with casted values
def castdicts(lst,key,_type):
    _type = _type.lower()
    if objname(lst) in {'list','tuple','set'}:
        for i in range(len(lst)):
            if _type in {'str','string'}:
                lst[i][key] = str(lst[i][key])
            elif _type in {'int','integer'}:
                lst[i][key] = int(lst[i][key])
            elif _type in {'float'}:
                lst[i][key] = float(lst[i][key])
        return lst
    raise ValueError

# Retrieves a list of filenames from a specifed directory
# @param string _dir = directory path
# @return [str] = list of filenames in a directory
def lsdir(_dir):
    f =[]
    for (dirpath,dirnames,filenames) in os.walk(_dir):
        f.extend(filenames)
        break
    return f

# Retrieves sud-directory names within a directory
# @param string _dir = directory path
# @return [str] = list of sub-directory names in a directory
def lssubdir(_dir):
    d = []
    for (dirpath,dirnames,filenames) in os.walk(_dir):
        d.extend(dirnames)
        break
    return d

# Delete all files in a directory and remove it
# @param string _dir = directory path
def deldir(_dir):
    if not os.path.exists(_dir):
        raise NotADirectoryError
    files = lsdir(_dir)
    for f in files:
        os.remove('%s/%s' % (_dir,f))
    os.removedirs(_dir)
    return

# Most Recent File
# @param string _dir = Directory
# @param regex ext = extension (i.e. r'*.json')
# @param bool lrf = Get the oldest file instead.
# @return string = the name of the most recent file in a directory
def mrf(_dir,ext=r'*.*',lrf=False):
    _file = glob.glob(os.path.join(_dir,ext))
    _file.sort(key=os.path.getctime,reverse=lrf)
    return _file[0]

# <!> NOT TESTED <!>
# Attempts to cast a string to a float or an int 
# @param string _str = A string
# @return _str or float(_str) or int(_str) 
def caststr(_str):
    # float
    if '.' in _str:
        try: _str = float(_str)
        except ValueError: pass
    # int
    else:
        try: _str = int(_str)
        except ValueError: pass
    # Otherwise it's a str
    return _str

# Nicely prints the first n objects in a list or tuple
# @param [] or () lst = list or tuple to preview
# @param int n (default 1) = Number of items to show 
def head(lst,n=1):
    if not objname(lst) in ['list','tuple']:
        raise ValueError
    if n >= len(lst):
        raise IndexError
    for item in lst[:n]:
        print(item)
    return

# Nicely prints the last n objects in a list or tuple
# @param [] or () lst = list or tuple to preview
# @param int n (default 1) = Number of items to show 
def tail(lst,n=1):
    if not objname(lst) in ['list','tuple']:
        raise ValueError
    if n >= len(lst):
        raise IndexError
    for item in lst[-n:]:
        print(item)
    return
    
# System Pause
def pause():
    return os.system('pause')
    
# Flatten Lists of Lists into a single list
# @param [[]] lst = a list of lists to flatten
# @param bool rm_none = Keeps empty lists when False
# @return [] = a flattened list
def flattenlist(lst,rm_none=True):
    flat_list = []
    for sublist in lst:
        if sublist == None:
            if not rm_none:
                flat_list.append(None)
        else:
            for item in sublist:
                flat_list.append(item)
        continue
    return flat_list

# Gets the current time
# @return The current time as a datetime object
def now():
    return datetime.datetime.now()

# Gets the elapsed time
# @param datetime _time = The point that is being measured from
# @return float = Time elapsed between now and _time in seconds.
def elapsed(_time):
    return (datetime.datetime.now() - _time).total_seconds()
