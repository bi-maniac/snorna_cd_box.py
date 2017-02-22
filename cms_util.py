#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys

#-------------------------------------------
#	Initialization & globals
#-------------------------------------------

#-------------------------------------------
#	Functions
#-------------------------------------------

def load_properties(ipfnap=False, arg=[]):
	"""Loads properties from file and overwrites from arg list

	Returns a dictionary with all properties"""

	dict = {}	# return variable
	pfname = ''	# properties file name
	ipf = False	# is there properties file?

	if ipfnap:	# is propreties file name, if given, a property?
		for argum in arg:
			if argum[:11] == 'properties=':
				ipf = True
				pfname=argum[11:]
	else:	# properties file name is assumed to be first arg
		ipf = True
		pfname = arg.pop(0)

	if ipf:
		dict = load_prop_file(pfname)
	else:
		#print(>>sys.stderr, 'No properties file')
		sys.stderr.write('No properties file\n')

	for argum in arg:
		if argum.count('=') == 0:
			pass	# invalid or empty line
		else:
			frg = argum.split('=')
			prp = frg[0].strip()
			val = frg[1].strip()
			dict[prp] = val
	return dict

#-------------------------------------------

def load_prop_file(filename):
	"""Loads a properties file

	Returns a dictionary with all properties"""

	dict = {}	# return variable
	p_line=''
	f = open(filename, 'r')
	for rec in f:
		if rec.count('#') == 0:
			p_line = rec
		else:
			p_line = rec[0:rec.find('#')]	# comments are deleted

		if rec.count('=') == 0:
			pass	# invalid or empty line
		else:
			frg = p_line.split('=')
			prp = frg[0].strip()
			val = frg[1].strip()
			dict[prp] = val
	f.close()
	return dict

#-------------------------------------------

def split_csv_line(line, field_separator, text_delimiter):
	"""Splits line into fields

	Gives text_delimiter precedence over field_separator"""

	sw = False
	string = ''
	fld = []
	for ix in range (len(line)):
		#print('char ', line[ix], 'sw', sw)
		if line[ix] == text_delimiter:
			if sw == False:
				sw = True
			else:
				sw = False
		else:
			if line[ix] == field_separator:
				if sw == True:
					string += line[ix]
				else:
					fld.append(string)
					string = ''
			else:
				string += line[ix]
		#print('char ', line[ix], 'sw', sw)
		#print()

	if len(string) > 0:
		fld.append(string)
	return fld

#-------------------------------------------
		
def extractLabelDelim(strg, label, occur=1):
	if (occur < 1):
		occur = 1
	dlm1=''
	dlm2=''
	if (strg.find('(') > -1):
		dlm1='('
		dlm2=')'
	elif (strg.find('[') > -1):
		dlm1='['
		dlm2=']'
	elif (strg.find('<') > -1):
		dlm1='<'
		dlm2='>'
	elif (strg.find('{') > -1):
		dlm1='{'
		dlm2='}'
	elif (strg.find('"') > -1):
		dlm1='"'
		dlm2='"'
	elif (strg.find("'") > -1):
		dlm1="'"
		dlm2="'"
	elif (strg.find('|') > -1):
		dlm1='|'
		dlm2='|'
	elif (strg.find('/') > -1):
		dlm1='/'
		dlm2='/'
	lbld = label+dlm1
	result = strg
	for ix in range(occur):
		result = result[result.find(lbld)+len(lbld):]
	result = result[:result.find(dlm2)]
	return(result)

#-------------------------------------------
		
def extractBalancedLevel(string, char, depth):
	ret = []
	if char == '[' or char == ']':
		c1 = '['
		c2 = ']'
	elif char == '(' or char == ')':
		c1 = '('
		c2 = ')'
	elif char == '{' or char == '}':
		c1 = '{'
		c2 = '}'
	elif char == '<' or char == '>':
		c1 = '<'
		c2 = '>'
	else:
		return ret

	lvl = 0
	strg = ''
	for c in string:
		if c == c1:
			lvl += 1
			if lvl > depth:
				strg += c
		elif c == c2:
			if lvl > depth:
				strg += c
			lvl -= 1

			if lvl == depth:
				ret.append(strg)
				strg = ''
		else:
			if lvl > depth:
				strg += c
	return ret

#===========================================
#	Test suite
#-------------------------------------------

if __name__ == '__main__':
	properties = load_prop_file('test.properties')
	print(properties)
	properties = {}
	properties = load_properties(False, ['test.properties', 'prop1=new_value_1'])
	print(properties)
	properties = {}
	properties = load_properties(True, ['properties=test.properties', 'prop1=new_value_1'])
	print(properties)
	properties = {}
	properties = load_properties(True, ['prop1=new_value_1'])
	print(properties)

	line = '"A","B","C"'
	result_list = split_csv_line(line, ',', '"')
	print()
	print(line)
	print(result_list)
	line = '"A,D","B","C"'
	result_list = split_csv_line(line, ',', '"')
	print()
	print(line)
	print(result_list)
	line = '"A\nD","B","C"'
	result_list = split_csv_line(line, ',', '"')
	print()
	print(line)
	print(result_list)
	line = '"A","B",C'
	result_list = split_csv_line(line, ',', '"')
	print()
	print(line)
	print(result_list)
	line = 'A,"B",C'
	result_list = split_csv_line(line, ',', '"')
	print()
	print(line)
	print(result_list)

	print()
	strg = 'type[delete] absIni1[81] str1[C] absIni1[82] str2[]'
	label = 'absIni1'
	value = extractLabelDelim(strg, label)
	print(value)

	print()
	s = '(((111())(222())(3()))(a a a a)(b b b)(c c)(d))'
	print(s)
	frg = extractBalancedLevel(s, '(', 0)
	print(frg)
	frg = extractBalancedLevel(s, '(', 1)
	print(frg)
	frg = extractBalancedLevel(s, '(', 2)
	print(frg)

#===========================================
