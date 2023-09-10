import copy
import fitz
import tempfile
import os

# Class to merge multiple source pdfs into one pdf
class Merge:
    def __init__(self, sources, rootDir):
        self.border = 20
        self.sources = sources
        self.name_tracker = []
        self.tmpPdf = fitz.open()
        self.spacing = 0
        self.rootDir = rootDir
        self.missingFiles = []
        self.max_size = 100 * 1024 * 1024 # 100 MB
        self.loadPages()

    # Loads all pages from the sources into the pages array
    def loadPages(self):
        # Sort the sources by the number of pages in the pdf, ignoring missing files
        try:
            self.sources.sort(key=lambda x: len(fitz.open(f"{self.rootDir}{x}")))
        except Exception as e:
            pass
        
        size = 0
        # Load all pages into the temporary pdf
        for paper in self.sources:
            path = f"{os.path.join(self.rootDir, paper)}" 
            try:
                if os.path.exists(path):
                    reader = fitz.open(path)

                    # If the file size is too big, don't add any more pages
                    size += len(reader.write())
                    if size > self.max_size:
                        break

                    # Add the pages to the temporary pdf
                    self.tmpPdf.insert_pdf(reader)

                    # Add the name of the paper to the name tracker
                    for page in reader:
                        self.name_tracker.append(paper)
                else:
                    raise FileNotFoundError
            # If the file doesn't exist, add it to the missing files list
            except IOError as e:
                self.missingFiles.append(paper)
                pass

        # If there are no pages, throw an error
        if len(self.tmpPdf) == 0:
            raise Exception("No pages were able to be loaded")


    # Merges all pages into one pdf, allowing for multiple smaller pages to be merged into one A4 page
    def mergePages(self):
        height = self.border
        pwidth, pheight = fitz.paper_size("a4")
        page_number = 0
    
        writer = fitz.open()
        out_page = writer.new_page(-1, width = pwidth, height = pheight)

        for index, input_page in enumerate(self.tmpPdf):
            
            # Every 10 pages, get the file size of the merged pdf
            if index % 10 == 0:
                size = len(writer.write())
                # If the file size is too big, don't add any more pages
                if size > self.max_size:
                    break

            # Get the height and rectangle of the current page
            cropbox = input_page.rect
            cur_height = cropbox.y1 - cropbox.y0

            # If the current page is too big to fit on the current page, add a new page
            if (cur_height + height) > pheight:
                out_page = writer.new_page(-1, width = pwidth, height = pheight)
                height = self.border
                page_number += 1
            
            # Get the rectangle where the page will be placed
            outbox = fitz.Rect(0, height, pwidth, height + cur_height)
            # Add the page to the buffer page
            out_page.show_pdf_page(outbox, self.tmpPdf, index, clip = cropbox)
            
            # Update the height
            height += cur_height + self.spacing

        # Write the merged pdf to a temporary file
        temp_file = tempfile.TemporaryFile()
        temp_file.write(writer.write())
        temp_file.seek(0)

        return temp_file, self.missingFiles
