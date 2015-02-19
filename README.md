These scripts are little modules to automate tiny-to (hopefully) large parts of my research workflow.

This is a summary of what exists in this repo so far:

Paper-Search:

Searches the papers in my local tree. Searches by title or entire document.
Uses XPDF package.

BibTeX URL Tack On:

Tacks on file paths as a 'Note' field to BibTeX entries in an existing BibTeX file, as urls.
Basically I realized this would be useful after having a lot of bib entries.
Uses Paper-Search to determine paths to papers, inserts the path in the note field, if using
correct packages (natbib hyperref) in LaTeX, this will make it so the references have links
to the files on the local machine (this specific script is terribly specific, but alterations wouldn't be hard).

TL;DR: Creates a clickable bibliography at the end of a paper so referenced papers can be opened with 1 click :D.

More to come!
