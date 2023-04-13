#remove PII data
# Usage: PRE-CONVERSION SCRIPT (if you want to change the original file contents)
# input: list_of_fields_to_check
# input: use_original_file (Original File must be selected)

list_of_fields_to_check= [] #for example: ["author","subject","message"], leave empty for all
use_original_file=True #Do we need to load the datastream to change the contents
badWords=["xxx","example.com"] #List of badwords to remove
log_field="log_pii" #field to record the log of the changes done
test = False #if you want to test it locally, not within an IPE

import re

#----------------------------------------------------
# All regex (compiled)
credentialIDSRegex = re.compile(r'''\b(username|login:|id|ccoid|u:)\s*:?\s*(?P<username>[\w\-\.@+]*)''', re.MULTILINE | re.VERBOSE | re.IGNORECASE)
credentialRegex = re.compile(r'''
        (username|login|id|u:)\s*:?\s*    # username might have : and whitespace
        (?P<username>[\w\-\.@+]*)      # capture the username for replacement
        \s+                            # some whitespace between
        (password|pw|p:)\s*:?\s*       # password might have : and whitespace
        (?P<password>.*)               # password can be anything until EOL
    ''', re.MULTILINE | re.VERBOSE | re.IGNORECASE)
creditcardRegex = re.compile((
        r"(?<=\s)"
        r"(?:4[0-9]{12}(?:[0-9]{3})?"  		# Visa
        r"|(?:5[1-5][0-9]{2}"          		# MasterCard
        r"|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}"
        r"|3[47][0-9]{13}"             		# American Express
        r"|3(?:0[0-5]|[68][0-9])[0-9]{11}"   	# Diners Club
        r"|6(?:011|5[0-9]{2})[0-9]{12}"      	# Discover
        r"|(?:2131|1800|35\d{3})\d{11})"      	# JCB
    ), re.VERBOSE)
ssnRegex = {
        'US': re.compile((
            r"[0-9][0-9][0-9]"  # first three digits
            r"[\-. ]"  # separator
            r"[0-9][0-9]"  # next two digits
            r"[\-. ]"  # separator
            r"[0-9][0-9][0-9][0-9]"  # last four digits
        ), re.VERBOSE),
        'GB': re.compile(
            r'(?!BG)(?!GB)(?!NK)(?!KN)(?!TN)(?!NT)(?!ZZ)(?:[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z])(?:\s*\d\s*){6}[A-D]',
            re.IGNORECASE | re.VERBOSE
        ),
    }
taxRegex = {
        'GB': re.compile(r'''\d{2}\s?[a-zA-Z]{1}(?:\s*\d\s*){5}''', re.IGNORECASE),
    }
driverRegex = {
        # this regex is looking for UK driving licence numbers that follow a pattern, no checksum
        'GB': re.compile(r'''([a-zA-Z9]{5}\s?)((?:\s*\d\s*){6}[a-zA-Z9]{2}\w{3})\s?(\d{2})''', re.IGNORECASE)
    }
emailRegex = re.compile((
        r"\b[a-z0-9!#$%&'*+\/=?^_`{|}~-]"             # start with this character
        r"(?:"
        r"    [\.a-z0-9!#$%&'*+\/=?^_`{|}~-]{0,62}"   # valid next characters (max length 64 chars before @)
        r"    [a-z0-9!#$%&'*+\/=?^_`{|}~-]"           # end with this character
        r")?"
        r"(?:@|\sat\s)"                               # @ or the word 'at' instead
        r"[a-z0-9]"                                   # domain starts like this
        r"(?:"
        r"    (?=[a-z0-9-]*(\.|\sdot\s))"             # A lookahead to ensure there is a dot in the domain
        r"    (?:\.|\sdot\s|[a-z0-9-]){0,251}"        # might have a '.' or the word 'dot' instead
        r"    [a-z0-9]"                               # domain has max 253 chars, ends with one of these
        r")+\b"
    ), re.VERBOSE | re.IGNORECASE)
regexPhone = re.compile(r"(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}")

replacements=[{"regex":credentialRegex,"text":"[CREDENTIAL]"},
{"regex":credentialIDSRegex,"text":"[CREDENTIAL]"},
{"regex":creditcardRegex,"text":"[CREDIT]"},
{"regex":ssnRegex['US'],"text":"[US_SSN]"},
{"regex":ssnRegex['GB'],"text":"[GB_SSN]"},
{"regex":taxRegex['GB'],"text":"[GB_TAX]"},
{"regex":driverRegex['GB'],"text":"[GB_DRIVER]"},
{"regex":emailRegex,"text":"[EMAIL]"},
{"regex":regexPhone,"text":"[PHONE]"},
]
#----------------------------------------------------
def get_safe_meta_data(meta_data_name):
    safe_meta = ''
    if test:
      meta_data_value = []
    else:
      meta_data_value = document.get_meta_data_value(meta_data_name)
    if len(meta_data_value) > 0:
        safe_meta = meta_data_value[-1]
    return safe_meta
#----------------------------------------------------
def removeWords(value):
  for word in badWords:
    value = re.sub(r'(?i)'+word, "[X]", value)
 
  return value
#----------------------------------------------------
def doCleaning(value):
  total_replacements=0
  log_data_cleaning=''
  for clean in replacements:
    value,no_of_replacements = re.subn(clean['regex'], clean['text'], value)
    if no_of_replacements>0:
      log_data_cleaning+=clean['text']+" "+str(no_of_replacements)+" \n"
    total_replacements+=no_of_replacements
  newvalue = removeWords(value)
  if newvalue!=value:
    log_data_cleaning+="\nRemoved bad words\n"
    total_replacements+=1
    value = newvalue
  return value, total_replacements, log_data_cleaning
#----------------------------------------------------
def cleanMetaData():
  total_no_of_replacements = 0
  log_data = ''
  fields=list_of_fields_to_check
  if len(list_of_fields_to_check)==0:
    if test:
      fields=[]
    else:
      fields = document.get_meta_data()
  for meta in fields:
    value = get_safe_meta_data(meta)
    if value:
      newvalue, no_of_replacements, log_data_cleaning = doCleaning(value)
      if no_of_replacements>0:
        log_data += log_data_cleaning
        document.add_meta_data({meta: newvalue})
        total_no_of_replacements+=no_of_replacements
  return total_no_of_replacements, log_data
#----------------------------------------------------
def cleanOriginal(text):
  total_no_of_replacements = 0
  log_data = ''
  initial_text = text
  if not test:
    binary_text = document.get_data_stream('documentdata')
    if binary_text is not None:
      raw_read_text = binary_text.read()
      try:
        initial_text = raw_read_text.decode()
      except:
        initial_text = raw_read_text.decode('iso-8859-1')
  if initial_text:
    newtext, no_of_replacements, log_data_cleaning = doCleaning(initial_text)

    if no_of_replacements > 0:
        total_no_of_replacements += no_of_replacements
        log_data = "\nChanged Original Document\n"+log_data_cleaning
        if not test:
          new_document = document.DataStream('documentdata')
          new_document.write(newtext)
          document.add_data_stream(new_document)
        else:
          #print(newtext)
          #print(log_data)
          writeFile('output.txt',newtext)
  return total_no_of_replacements, log_data

#----------------------------------------------------
def readFile(filename):
  with open(filename, 'r', encoding='UTF8', newline='') as f:
    return f.read()
def writeFile(filename, contents):
  with open(filename, 'w', encoding='UTF8', newline='') as f:
    return f.write(contents)

#----------------------------------------------------
_total_no_of_replacements=0
_log_data=''

total_no_of_replacements, log_data=cleanMetaData()
_total_no_of_replacements += total_no_of_replacements
_log_data+= log_data

if use_original_file:
  total_no_of_replacements, log_data=cleanOriginal('')
  _total_no_of_replacements += total_no_of_replacements
  _log_data+= log_data

_log_data="Total no of replacements: "+str(_total_no_of_replacements)+"\n"+_log_data

if not test:
  document.add_meta_data({log_field: _log_data})
else:
  pass
  # file1 = readFile('testfile1.txt')
  # #print(file1)
  # total_no_of_replacements, log_data=cleanOriginal(file1)
  # print(log_data)
  # file2 = readFile('testfile2.html')
  # total_no_of_replacements, log_data=cleanOriginal(file2)
  # print(log_data)
