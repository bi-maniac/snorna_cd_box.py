#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""Reads a fasta file, containing Small Nucleolar RNA (SNORNA) sequences, and search motives
in them. If an output file is provided, found motives are annotated in each sequence label"""

import re
import sys
import cms_bi
import cms_util

#-------------------------------------------
#	Functions
#-------------------------------------------

def help_text():
	print('Syntax:\n'+sys.argv[0]+' [PropertyName=PropertyValue]...')
	print('\tMandatory properties:')
	print('\t\tinfile: target file')
	print('\t\tcboxfile: cbox motives file')
	print('\t\tdboxfile: dbox motives file')
	print('\t\tannot_type: plexy|...')
	print('\t\tstructures: 1 to N separated by comma structures as follows')
	print('\t\t\tCbox|Dbox|<nuc_amt_range>|[Cbox|Dbox|<nuc_amt_range>]... '+
	'[,Cbox|Dbox|<nuc_amt_range>|[Cbox|Dbox|<nuc_amt_range>]]...')
	print('\t\t\t\tnuc_amt_range means nucleotides amount range and is expressed <min-max>')
	print('\t\t\texample:')
	print('\t\t\t\t<4-20>Cbox<10-100>Dbox<4-120>,<4-120>Cbox<11-101>Dbox<12-102>Cbox<13-103>Dbox<4-120>')
	print('\tOptional properties:')
	print('\t\tproperties: properties file')
	print('\t\toutfile: target file annotated\n')
	return

#-------------------------------------------

def load_structures(struct_string):
	global struct_arr

	struct_arr = []			# supports N alternative structures
	frgs = struct_string.split(',')	# separated by comma
	for frg in frgs:
		sfrgs = re.split('<|>', frg)
		struc = []		# a new structure is initialized
		for sfrg in sfrgs:
			if len(sfrg) > 0:
				elem = ()	# a new element is initialized and defined as tuple '()'
				# elements can have an alphabetic item: 'cbox' or 'dbox'
				# or 2 numeric item, separated by '-', meaning a range of nucleotide length
				sfrg = sfrg.lower()
				if sfrg == 'cbox' or sfrg == 'dbox':
					elem = (sfrg)	# tuple with only 1 item
				elif re.match('[0-9]+-[0-9]+', sfrg):
					f = sfrg.split('-')
					elem = (int(f[0]), int(f[1]))	# tuple with 2 items
				else:
					print('ERROR', sfrg)
				struc.append(elem)

		struct_arr.append(struc)

	return

#-------------------------------------------

def load_motives(filename):
	mot_list = []
	boxfile = open(filename, 'r')
	rec = boxfile.readline()
	while rec:
		rec = rec.rstrip('\n')
		mot_list.extend(cms_bi.expand_wildcards(rec))
		rec = boxfile.readline()

	return mot_list

#-------------------------------------------

def gen_cand_marks(range_tuple, box_typ, tseq, cand_mark_arr):
	global cbox, dbox
	new_cm_arr = []

	for itm1 in cand_mark_arr:
		cand_seq = itm1[0]
		mark_str = itm1[1]

		box_arr = []
		if box_typ == 'cbox':
			box_arr = cbox
		elif box_typ == 'dbox':
			box_arr = dbox
		elif box_typ == 'END':
			lsl = len(tseq) - len(cand_seq)	# last segment length
			if lsl >= range_tuple[0] and lsl <= range_tuple[1]:
				cma_item = tseq+mark_str	# total sequence is accepted
				new_cm_arr.append(cma_item) 

		else:
			print('ERROR box_typ:', box_typ)

		for box in box_arr:
			bx = len(cand_seq)	# base index, to skip subseq already accepted as candidate
			ix = bx + range_tuple[0]
			while ix < len(tseq) and ix <= (bx + range_tuple[1]):
				ix = tseq.find(box, ix)
				if ix == -1:
					break
				new_cand = tseq[:ix]+box	# elongated new candidate
				lnc = len(new_cand) - len(box)	# new candidate length
				cma_item = (new_cand , mark_str+'_'+box+'-'+str(lnc +1))	# mark is base 1
				new_cm_arr.append(cma_item) 
				ix += len(box)

	return new_cm_arr

#-------------------------------------------

def process_seq(lbl, seqlines):
	global cntseq, cntout, boolof, outfile

	tline = ''
	cntseq += 1

	tline = ''.join(seqlines)       # output will be a 1 line per sequence .fa

	for struct in struct_arr:
		last_range = (0, 0)     # last segment of length range type
		lass = 0	# last assessed segment in struct
		# These 2 arrays go in parallel
		cand_mark_arr = [('','')]       # each item is a tuple with a sequence and a mark_str

		for segment in struct:
			if len(segment) == 2:
				last_range = segment
			elif segment == 'cbox' or segment == 'dbox':
				cand_mark_arr = gen_cand_marks(last_range, segment, tline, cand_mark_arr)
			else:
				print('ERROR segment:', segment)

		# last segment of each struct uses to be of length range type
		if len(segment) == 2:
			cand_mark_arr = gen_cand_marks(last_range, 'END', tline, cand_mark_arr)

		print('\nResults for struct', struct)
		for item in cand_mark_arr:
			frg = item.split('_', 1)
			print(frg[0], frg[1])

			if boolof:
				if annot_type == 'plexy':
					outfile.write(lbl+'_'+frg[1].replace('-', '_')+'\n')
					outfile.write(tline+'\n')       # modificar si se quiere respetar las líneas de entrada
					cntout += 2
				#elif annot_type == 'xxxx':	# otros tipos de anotación
				else:
					print('ERROR annotation type is not valid:', annot_type)

	return

#-------------------------------------------
#	Initialization & globals
#-------------------------------------------

boolof = False	# boolean output file
prop_dict = {}	# to store all properties
struct_arr = []	# to store structures to match

if len(sys.argv) > 1:
	if sys.argv[1] == '-h' or sys.argv[1] == '--help':
		help_text()
		exit(10)
	else:
		prop_dict = cms_util.load_properties(True, sys.argv)
		print(prop_dict)
else:
	help_text()
	exit(10)

cntin = 0
cntout = 0
cntseq = 0
cbox = []	# list to store cbox motives
dbox = []	# list to store dbox motives

#-------------------------------------------
#	Process
#-------------------------------------------

load_structures(prop_dict["structures"])
print('structures array:', struct_arr)

cbox = load_motives(prop_dict['cboxfile'])
dbox = load_motives(prop_dict['dboxfile'])

lbline = ''
seqlines = []
infile = open(prop_dict['infile'], 'r')

if 'outfile' in prop_dict:
	outfile = open(prop_dict['outfile'], 'w')
	boolof = True
else:
	boolof = False
print ('dbg1 boolof', boolof)

annot_type =  prop_dict['annot_type']

rec = infile.readline()
while rec:
	rec = rec.rstrip('\n')
	cntin += 1
	if cntin == 1:
		if rec.startswith('>'):
			lbline = rec
		else:
			print('Input file '+ifilename+' is not fasta format')
			exit(10)
	else:
		if rec.startswith('>'):
			process_seq(lbline, seqlines)
			seqlines = []
			lbline = rec
		else:
			seqlines.append(rec)

	rec = infile.readline()

process_seq(lbline, seqlines)

infile.close()
if boolof:
	outfile.close()

print('----------------------')
print('Input records:', cntin)
print('Input sequences:', cntseq)
if boolof:
	print('Output records:', cntout)
print('----------------------')
print('OK')
print('----------------------')

exit(0)
