#/bin/python3.4

import argparse
import os
import subprocess
import sys
from re import search

###############################---------------Constants---------#####################
PREVIEW_SIZE = 120
#####################################################################################

#Counts the number of lines in the passed in text file
#Returns the number of lines in the file
def num_file_lines(full_file_path):

    return len(open(full_file_path, 'r').read().splitlines())

#Searches the passed in pdf file_name for lines containing keyword
#Returns a list of matches, 
    #each match is a tuple with: (PREVIEW OF MATCHED REGION, LINE NUMBER, COLUMN NUMBER)
def search_pdf_file(keyword, 
                    full_file_path,
                    case_sensitive=False):
    
    global PREVIEW_SIZE

    FOUR_SPACES = "    "
    
    #run pdftotext (from xpdf pacakge) on the pdf file to convert to text
    subprocess.call(['pdftotext', '-layout', full_file_path])

    #Stores tuples of surrounding text, line number, and column
    matches = []    

    temp_text_full_file_path = full_file_path[:-4] + ".txt" 

    with open(temp_text_full_file_path, 'r') as temp:

        temps_lines = temp.read().splitlines()

        for line_num in range(0, len(temps_lines)):   
            
            line = temps_lines[line_num]

            keyword_index = line.lower().find(keyword.lower()) if not case_sensitive else line.find(keyword)

            if keyword_index != -1:

                #Determine column
                spaces_index = line.find(FOUR_SPACES)
                if spaces_index < keyword_index:

                    col_num = 2

                else:

                    col_num = 1

                #Get surrounding text

                #Get previous text, including other lines
                pre_line_text = ""
                temp_keyword_index = keyword_index
                cur_line_num = line_num
                remaining_size = PREVIEW_SIZE // 2
                while remaining_size > 0\
                        and cur_line_num > 0:

                    beg_index = max(0, (len(temps_lines[cur_line_num]) - remaining_size))
                    end_index = temp_keyword_index
                    cur_line_text = temps_lines[cur_line_num][beg_index:end_index].strip() + ' '
                    pre_line_text = cur_line_text + pre_line_text

                    if cur_line_num != 0:
                        temp_keyword_index = len(temps_lines[cur_line_num - 1])

                    remaining_size -= len(cur_line_text)
                    cur_line_num -= 1

                #Get next text, including other lines
                post_line_text = ""
                temp_keyword_index = keyword_index
                cur_line_num = line_num
                remaining_size = PREVIEW_SIZE // 2
                while remaining_size > 0\
                        and cur_line_num < len(temps_lines):

                    beg_index = temp_keyword_index
                    end_index = min(len(temps_lines[cur_line_num]), beg_index + remaining_size)
                    cur_line_text = ' ' + temps_lines[cur_line_num][beg_index:end_index].strip()
                    post_line_text += cur_line_text

                    temp_keyword_index = 0

                    remaining_size -= len(cur_line_text)
                    cur_line_num += 1

                #Construct and process preview string
                preview_string = pre_line_text + post_line_text
                preview_string = preview_string.replace('\n', ' ')
                preview_string = preview_string.strip()

                #Remove big chunks of spaces....
                i = 0
                while i < len(preview_string):

                    c = preview_string[i]

                    if c == ' ':
                        
                        j = i + 1
                        while preview_string[j] == ' ':

                            j += 1

                        preview_string = preview_string[:(i + 1)] + preview_string[j:]

                    i += 1

                matches.append((preview_string, line_num, col_num))

    #Remove the temp text file
    #os.remove(temp_text_full_file_path)

    return matches


def search_tree(keyword, 
                base_path=os.path.expanduser("~") + '/grad-docs/research/papers', 
                search_by_title=True, 
                search_all_text=False,
                case_sensitive=False):

    #Stores tuples of format (FILE NAME, [LIST OF MATCHES])
    all_matches = []

    for cur_file in os.listdir(base_path):

        full_file_path = base_path + "/" + cur_file

        #Dive into directories
        if os.path.isdir(full_file_path):

            all_matches = all_matches + search_tree(keyword=keyword,
                                                    base_path=full_file_path,
                                                    search_by_title=search_by_title,
                                                    search_all_text=search_all_text,
                                                    case_sensitive=case_sensitive)
        #Handle files
        else:

            #If this file has a pdf extension
            if cur_file.lower().find('.pdf') == (len(cur_file) - 4):

                #Search all pdf text
                if search_all_text:
                    
                    cur_file_matches = search_pdf_file(keyword, full_file_path)
                    if len(cur_file_matches) > 0:
                        all_matches.append((cur_file, cur_file_matches))

                #Search by title
                else:

                    #Case sensitivity
                    if not case_sensitive:
                        keyword_index = cur_file.lower().find(keyword.lower())
                    else:
                        keyword_index = cur_file.find(keyword)

                    #if keyword found
                    if keyword_index != -1:
                        all_matches.append((cur_file, []))

    return all_matches

#Acts upon the search options passed, applies them to the search_tree function
#Returns a list of all the results
    #The list is in the format [(SUBJECT, [SEARCH RESULTS])]
        #The subject may be None if all subjects are searched
def search_setup(keyword, 
                    base_path=os.path.expanduser("~") + '/grad-docs/research/papers',
                    subjects=[],
                    search_by_title=True,
                    search_all_text=False,
                    case_sensitive=False):

    subject_to_folder_map = subject_to_folder_mapping(base_path)
    all_results = []

    if len(subjects) != 0:

        #Loop over each subject
        for subject in subjects:

            folder = subject_to_folder_map[subject]

            #Append a tuple with the subject and the results under that subject
            all_results.append((subject, search_tree(keyword, 
                                                        base_path + "/" + folder,
                                                        search_by_title,
                                                        search_all_text,
                                                        case_sensitive)))

    else:

        all_results.append((None, search_tree(keyword,
                                                base_path,
                                                search_by_title,
                                                search_all_text,
                                                case_sensitive)))

    return all_results

#Get all of the papers into a list (a paper must be a .pdf extension having file)
#Return the list
def get_all_papers(base_path=os.path.expanduser("~") + '/grad-docs/research/papers'):

    papers = []

    for cur_file in os.listdir(base_path):

        cur_full_file_path = base_path + "/" + cur_file

        if os.path.isdir(cur_full_file_path):

            papers = papers + get_all_papers(cur_full_file_path)

        else:

            if search(".pdf$", cur_file):
                papers.append(cur_file)

    return papers

#Since I am stubborn and refuse to give up my spaces in my folder names
#I need a mapping from the subjects to the folder names to avoid ambiguity
def subject_to_folder_mapping(base_path=os.path.expanduser("~") + '/grad-docs/research/papers'):
    
    folders = get_all_folders(base_path)
    subjects = folders_to_subjects(folders)

    mapping = {}

    for s, f in zip(subjects, folders):
        mapping[s] = f

    return mapping

#Convert all spaces to dashes in a list of strings
def space_to_dash(list_of_strings):
    return [x.replace(' ', '-') for x in list_of_strings]

#COnvert all instances of a '/' with a '--' in a list of strings
def slash_to_double_dash(list_of_strings):
    return [x.replace('/', '--') for x in list_of_strings]

#Convert folders to subjects format (no spaces (replaced by dashes), all lowercase)
def folders_to_subjects(folders):

    folders = space_to_dash(folders)
    folders = slash_to_double_dash(folders)
    return [x.lower() for x in folders]

#Get a list of all of the folders under base_path
#Return the list of all folders
def get_all_folders(base_path=os.path.expanduser("~") + '/grad-docs/research/papers', 
                        cur_folder=None):

    folders = []

    for cur_file in os.listdir(base_path):

        cur_full_file_path = base_path + "/" + cur_file

        if os.path.isdir(cur_full_file_path):

            #Handle 'sub-folders'
            if cur_folder is not None:
                folders.append(cur_folder + "/" + cur_file)
            else:
                folders.append(cur_file)

            folders = folders + get_all_folders(cur_full_file_path, cur_file)

    return folders

#Get a list of all of the subjects
    #(a subject is an all lowercase folder name with spaces replaced with dashes containing papers)
#Return the list of all subjects
def get_all_subjects(base_path=os.path.expanduser("~") + '/grad-docs/research/papers',
                        cur_subject=None):

    mapping = subject_to_folder_mapping(base_path)
    cur_folder = mapping[cur_subject] if cur_subject is not None else None
    return folders_to_subjects(get_all_folders(base_path, cur_folder))
    
def print_results(search_results):

    print("\nPRINTING RESULTS************************************************************")
    
    #Loop over subjects
    for result_tuple in search_results:

        subject = result_tuple[0]
        subject_results = result_tuple[1]

        #Print subject
        if subject is not None:
            
            print('\n{: <10} -------- {: <40}'.format("Subject:", str(subject)))
            print('===========================================================================')

        #Loop over subject results
        for subject_result_tuple in subject_results:

            file_name = subject_result_tuple[0]
            file_search_results = subject_result_tuple[1]

            print('\n{: <10} -------- {: <100}'.format("File Name:", file_name))
            print('-----------------------------------------------------------------------')

            #Loop over inner file results
            for file_search_result in file_search_results:

                preview = file_search_result[0]
                line_num = file_search_result[1]
                col_num = file_search_result[2]

                print('{: <160} \t {: <5} \t {: <1}'.format(preview, line_num, col_num))

    print("")


#Handle all of the command processing, direct traffic, etc
def front_end(base_path=os.path.expanduser("~") + '/grad-docs/research/papers'):

    parser = argparse.ArgumentParser(description='Search through my academic papers.')
    parser.add_argument('-s', 
                        dest='subjects', 
                        action='append', 
                        default=[], 
                        choices=get_all_subjects(base_path))
    parser.add_argument('-a', 
                        dest='list_all_subjects', 
                        default=False,
                        action='store_true')
    parser.add_argument('-p', 
                        dest='list_all_papers', 
                        default=False,
                        action='store_true')
    parser.add_argument('-c',
                        dest='count_of_papers',
                        default=False,
                        action='store_true')
    parser.add_argument('-t', 
                        dest='search_by_title', 
                        default=True, 
                        action='store_true')
    parser.add_argument('-w', 
                        dest='search_all_text', 
                        default=False, 
                        action='store_true')
    parser.add_argument('-b', 
                        dest='base_path', 
                        default=base_path)
    parser.add_argument('-C',
                        dest='case_sensitive',
                        default=False,
                        action='store_true')
    parser.add_argument(dest='keyword', 
                        nargs='+')
    args = parser.parse_args()

    print("\n" + str(args) + "\n")
    print("Keyword: " + ' '.join(args.keyword) + "\n")

    #List all subjects and exit
    if args.list_all_subjects:
        print("\nSubjects Found:\n")
        all_subjects = get_all_subjects(base_path)
        sorted_all_subjects = sorted(all_subjects)
        for subject in sorted_all_subjects:
            print(subject)
        print("")
        return

    #List all papers and exit
    if args.list_all_papers:
        print("\nPapers Found:\n")
        all_papers = get_all_papers(base_path)
        sorted_all_papers = sorted(all_papers)
        for paper in sorted_all_papers:
            print(paper)
        print("")
        return

    if args.count_of_papers:
        print("\nThere are %d papers.\n" % (len(get_all_papers(base_path))))
        return

    if args.keyword is not None:

        #Run Searches
        search_results = search_setup(' '.join(args.keyword), 
                                        args.base_path, 
                                        args.subjects, 
                                        args.search_by_title, 
                                        args.search_all_text,
                                        args.case_sensitive)

        #Print results
        print_results(search_results)

    else:
        print("\nYOU MUST HAVE A KEYWORD TO SEARCH BY!\n")

if __name__ == '__main__':
    front_end("/home/egaebel/grad-docs/research/papers")
