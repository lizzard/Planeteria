#!/usr/bin/python
"""
Planeteria admin interface
Copyright 2009 James Vasile <james@hackervisions.org>
Released under AGPL, version 3 or later <http://www.fsf.org/licensing/licenses/agpl-3.0.html>

Utility functions
"""

import os, sys, dbm, time
import htmltmpl # Debian package python-htmltmpl
import tidy
from config import *

generated=[]

def html2xml(ins):
   """replace all the html entities with xml equivs"""
   ins = ins.replace("&nbsp;", "&#160;")
   return ins


def parse_updated_time(entry):
   try:
      return time.mktime(time.strptime(entry['updated'], "%a, %d %b %Y %H:%M:%S +0000"))
   except ValueError:
      return 0

def just_body(xhtml):
   return str(xhtml).split(' <body>')[1].split(' </body>')[0]

class berkeley_db:
   def __init__(self, fname):
      self.fname = fname
   def __enter__(self):
      self.db = dbm.open(os.path.join(DATA_DIR, self.fname), 'c')
      return self.db
   def __exit__(self, type, value, traceback):
      self.db.close()


def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
   """From django, mildly modified. TODO: check license"""
   """Returns a bytestring version of 's', encoded as specified in 'encoding'.

   If strings_only is True, don't convert (some) non-string-like objects. 
   """
   if not isinstance(s, basestring):
      try:
         return str(s)
      except UnicodeEncodeError: 
         return unicode(s).encode(encoding, errors)
   elif isinstance(s, unicode):
      return s.encode(encoding, errors)
   elif s and encoding != 'utf-8': 
      return s.decode('utf-8', errors).encode(encoding, errors) 
   else: 
      return s 

def merge_dict(a, b):
   """Return a hash containing all the keys and vals of a and all
   those of b that don't clash with a.  Modifies a in place and also
   returns a"""
   for k in b.keys():
      if a.has_key(k): continue
      else: a[k] = b[k]
   return a

def dict_val(dict, key):
   "Returns dict[key], but if key isn't present, returns a blank string"
   try:
      return dict[key]
   except KeyError:
      return ''

def write_file(dir, fname, string):
   "Opens a fname in dir for writing, writes string, closes fname"
   with open(os.path.join(dir, fname),"w") as FILE:
      FILE.write(string)

def write_add(output_dir, output_fname, contents):
   """Do a write_file and add to list of generated files"""
   write_file(output_dir, output_fname, contents)
   generated.append(os.path.join(output_dir, output_fname))

def interpolate(template, vals):
   "apply the keys and values in vals to template, return filled-in template"
   try:
      print template_vars['base_href']
   except:
      pass

   manager = htmltmpl.TemplateManager()
   template = manager.prepare(template)
   tp = htmltmpl.TemplateProcessor(html_escape=0)
   for key in vals:
      try:
         if isinstance(vals[key], basestring):
            tp.set(key, smart_str(vals[key], encoding='ascii', errors='ignore'))
         elif vals[key]:
            tp.set(key, vals[key])

      except:
         pass
   return tp.process(template)

def tidy2xhtml(instr):
   options = dict(output_xhtml=1,
                  add_xml_decl=0,
                  indent=1
                  )
   tidied = tidy.parseString(instr, **options)
   return tidied


def make_static(output_dir, output_fname, template_fname, template_vars):
   template_fname = os.path.join(TEMPLATE_DIR, template_fname)
   try:
      os.unlink(template_fname + "c")
   except:
      pass
   write_add(output_dir, output_fname, interpolate(template_fname, template_vars))

def make_page(name):
   "Make a standard page in the httproot"
   make_static(OUTPUT_DIR, "%s.html" % name, "%s.tmpl" % name, opt)