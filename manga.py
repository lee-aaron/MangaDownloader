try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin
import requests
import os
import glob
import shutil
import img2pdf
from bs4 import BeautifulSoup

source = [
    "https://www.mangatown.com/manga/",
    "http://www.mangareader.net/"
]

class Downloader:
    # This class contains the methods used to scrape the mangatown website and download the images

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36"}

        requests.packages.urllib3.disable_warnings()  # turn off SSL warnings

    def visit_main_url(self, url, manganame):

        content = self.session.get(url, verify=False).content
        soup = BeautifulSoup(content, "lxml")
        mangalist = soup.find(
            'ul', attrs={'class', 'chapter_list'}).find_all('a')

        mangalist.reverse()

        # visit each chapter link; skip pdfs already converted
        for item in mangalist:
            if os.path.exists(manganame + "/" + item['href'][2:-1].split("/")[-1] + ".pdf"):
                print(manganame + "/" + item['href'][2:-1].split("/")[-1] + ".pdf" + " already downloaded")
                continue
            self.visit_chapter(source[0] + item['href'][2:].split("/",2)[2], manganame)

    def visit_chapter(self, url, manganame):

        req = self.session.get(url, verify=False)
        if req.status_code == 200:
            soup = BeautifulSoup(req.text, 'lxml')

            # Make chapter directory
            self.make_directory(manganame + "/" + url.split("/")[-2])

            # Get only one list of the available pages
            pagelist = soup.find('select', {'onchange':'javascript:location.href=this.value;'}).find_all('option')

            # Each page except last one which is a featured page
            for item in pagelist[:-1]:
                self.visit_page(source[0] + item['value'][2:].split("/",2)[2], manganame + "/" + url.split("/")[-2])
            
            # Convert images in folder to PDF
            self.make_pdf(manganame + "/" + url.split("/")[-2])
            
    def visit_page(self, url, dirname):

        req = self.session.get(url, verify=False)
        if req.status_code == 200:
            soup = BeautifulSoup(req.text, 'lxml')
            # Find img links in the page url
            self.download_image(soup.find('img')['src'], dirname)

    def download_image(self, image_url, dirname):
        '''
        Downloads image to local subdirectory path
        '''
        local_filename = image_url.split('/')[-1].split("?")[0]

        # Write to directory + filename
        r = self.session.get(image_url, stream=True, verify=False)
        with open(
            os.path.join(
                dirname, local_filename), 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)
    
    def make_directory(self, name):

        if not os.path.exists(name):
            os.makedirs(name)
    
    def make_pdf(self, directory):
        # imagelist is the list of images in directory
        # pdfname is the chapter name
        imagelist = glob.glob(directory + "/*.jpg")
        pdfname = directory.split("/")[1] + ".pdf"

        # All images should be in [Name of manga]/[chapter #] dir
        with open(directory.split("/")[0] + "/" + pdfname, "wb") as f:
            f.write(img2pdf.convert(imagelist))
        
        # Removes folder with images
        if os.path.exists(directory):
            shutil.rmtree(directory)

def mangareader(url: str):
    # TODO: implement support for mangareader
    req = requests.get(url, timeout=10, verify=False)

    if req.status_code == 200:
        soup = BeautifulSoup(req.text, 'lxml')
        mangalist = soup.find_all(
            'div', attrs={'class', 'chico_manga'})
            
            #find_all(
            #    'div', attrs={'class', 'chico_manga'}).find_all(
            #        'a')
            
        print(mangalist)

def main():
    download = Downloader()
    manga = input("Enter manga name: ")
    linkname = manga.lower().replace(" ", "_")
    download.make_directory(manga)
    download.visit_main_url(source[0] + linkname, manga)
    # mangareader(source[1] + "yamada-kun-to-7-nin-no-majo")

if __name__ == '__main__':
    main()