#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
# Just in case BioPython is not installed
try:
	from Bio.Data import IUPACData
	iupac_adv = IUPACData.ambiguous_dna_values 
except ImportError:
	iupac_adv = {
		"A": "A",
		"C": "C",
		"G": "G",
		"T": "T",
		"M": "AC",
		"R": "AG",
		"W": "AT",
		"S": "CG",
		"Y": "CT",
		"K": "GT",
		"V": "ACG",
		"H": "ACT",
		"D": "AGT",
		"B": "CGT",
		"X": "GATC",
		"N": "GATC", 
	} 

#-------------------------------------------
#	Initialization & globals
#-------------------------------------------

#-------------------------------------------
#	Functions
#-------------------------------------------

def expand_wildcards(seq):
	bl = [seq]
	for ix in range(len(seq)):
		bool = True
		while bool:
			iseq = bl.pop(0)
			sl = list(iseq)
			v = iupac_adv[sl[ix]]
			if len(v) == 1:
				bool = False
				bl.append(iseq)
			else:
				for jx in range(len(v)):
					sl[ix] = v[jx]
					iseq = (''.join(sl))
					bl.append(iseq)

	bl.sort()	# no need, in fact
	return bl


#===========================================
#	Test suite
#-------------------------------------------

if __name__ == '__main__':
	result = expand_wildcards('ASN')
	print(result)
#-------------------------------------------
