#/bin/python3.4

#Hacky fix to make sibling imports work...I like it.
import sys; import os
sys.path.insert(0, os.path.abspath('..'))
###################################################

#My Modules
from paper_search_script import paper_search

from collections import OrderedDict

MULTIPLE_FILES_FOUND_MESSAGE = "------------------------MULTIPLE FILES FOUND---------------------------------"
FAILURE_TO_FIND_FILE_STRING = "COULD NOT FIND FILE"
COMMA = ','
ENDLINE = '\n'

#parse bib file
#Return list of dictionaries, one dictionary per bibtex entry
def parse_bib(bib_file_name):
	
	with open(bib_file_name, 'r') as bib_file:
	
		entries = []
		entry_dict = OrderedDict()
		count = 0
		for line in bib_file:

			if line.isspace() or line.strip().find('%') == 0:
				continue

			if line.find('@') == 0:
				entry_dict['heading_tag'] = line
			elif line.find('}') == 0:
				entry_dict['tail_tag'] = line
				entries.append(entry_dict)
				entry_dict = OrderedDict()
			else:
				#Rip the bibtex title to set as key
				temp_key = line.strip().split(' ')[0]
				entry_dict[temp_key] = line

			count += 1

		return entries


def get_paper_path(paper_title):
	
	global FAILURE_TO_FIND_FILE_STRING
	global MULTIPLE_FILES_FOUND_MESSAGE

	#Perform a case sensitive search using the paper_search.py module
	packaged_search_results = paper_search.search_setup(keyword=paper_title)
	search_results = packaged_search_results[0]['subject_results']

	if len(search_results) > 1:
		for r in search_results:
			print(r)
			print(r['file_name'] + ' at ' + r['file_path'])
		print(MULTIPLE_FILES_FOUND_MESSAGE)
		return FAILURE_TO_FIND_FILE_STRING
	elif len(search_results) == 0:
		print("No results found")
		return FAILURE_TO_FIND_FILE_STRING
	else:
		result = search_results[0]
		print(result['file_name'] + ' at ' + result['file_path'])
		return result['file_path']

def write_back_bibtex(bib_file_name, entries):

	global COMMA
	global ENDLINE

	with open(bib_file_name, 'w') as bib_file:

		for entry_dict in entries:
			key_count = 0
			keyset = entry_dict.keys()
			for key in keyset:
				value = entry_dict[key]
				if key_count < (len(keyset) - 2):
					if value.strip()[len(value.strip()) - 1] != COMMA:
						if value[len(value) - 1] == ENDLINE:
							value = value[:(len(value) - 1)]
						value += COMMA
						value += ENDLINE
				bib_file.write(value)
				key_count += 1
			bib_file.write(ENDLINE)

def add_field_to_entries(bib_file_name):

	global FAILURE_TO_FIND_FILE_STRING

	entries = parse_bib(bib_file_name)
	for entry_dict in entries:
		
		paper_title = entry_dict['Title']
		paper_title_beg_index = paper_title.find('{')
		paper_title_end_index = paper_title.find('}')
		paper_title = paper_title[(paper_title_beg_index + 1):paper_title_end_index]

		paper_path = get_paper_path(paper_title)

		if paper_path != FAILURE_TO_FIND_FILE_STRING:

			#Adjust path to fit relative location of outline
			papers_str = 'papers/'
			papers_index = paper_path.find(papers_str)
			paper_path = paper_path[(papers_index + len(papers_str)):]

			paper_path = 'Link to papers/' + paper_path

			entry_dict['Note'] = '  Note                     = {{\\url{%s}}}\n' % paper_path
			entry_dict.move_to_end('tail_tag')
								

	#Remove after testing (or maybe never since shit breaks)
	bib_file_name += '.test'

	#Testing for OrderedDict keyset iteration
	for entry_dict in entries:
		for key in entry_dict.keys():
			print(str(key) + ' : ' + str(entry_dict[key]))

	write_back_bibtex(bib_file_name, entries)


#front end, parsing, data flow, etc
def front_end():
	add_field_to_entries('/home/egaebel/grad-docs/research/papers/papers-db--02-18-2015.bib.bak')

if __name__ == '__main__':
	front_end()