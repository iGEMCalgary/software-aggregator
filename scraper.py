from html.parser import HTMLParser

import requests
import nltk
from bs4 import BeautifulSoup


class htmlEraser(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


class Scraper():
    def eraseTags(self, text):
        eraser = htmlEraser()
        eraser.feed(text)
        return eraser.get_data()

    def getSoftwareLinks(self, year, progress):
        links = []
        linksWithSoftware = []
        try:
            source = requests.get('http://igem.org/Team_Wikis?year=' + str(year)).text
        except requests.exceptions.ConnectionError:
            print("Connection error!")
        except Exception as e:
            print(e)
        soup = BeautifulSoup(source, 'lxml')
        content = soup.find('div', id='content_Page')
        # progress.emit(10)
        import time

        sentenceWithTotal = content.find('big').text
        splitSentence = sentenceWithTotal.split(" ")
        total = int(splitSentence[0])
        print(total)
        start = time.time()
        for wiki in content.findAll('a'):
            links.append(wiki['href'] + "/Software")
        print(time.time() - start)
        for i in range(0, len(links), 1):
            wikiSource = requests.get(links[i]).text
            if "There is currently no text in this page." in wikiSource or \
                    "In order to be considered for the" in wikiSource or \
                    "you must fill this page." in wikiSource or \
                    "This page is used by the judges to evaluate your team for the" in wikiSource or \
                    "Regardless of the topic, iGEM projects often create or adapt computational tools to move the " \
                    "project forward." in wikiSource:
                pass
            else:
                linksWithSoftware.append(links[i])
            # progress.emit(20 / len(links))
        return linksWithSoftware

    def getSoftwareData(self, year, progress):
        softwareData = []
        softwareLinks = self.getSoftwareLinks(year, progress)
        for i in range(0, len(linksWithSoftware), 1):
            softwareWikiSource = requests.get(linksWithSoftware[i]).text
            soup = BeautifulSoup(softwareWikiSource, 'lxml')
            for tag in soup():
                for attribute in ['class', 'id', 'name', 'style']:
                    del tag[attribute]
            [tag.decompose() for tag in soup("style")]
            [tag.decompose() for tag in soup("script")]
            content = soup.find('body')
            content = self.eraseTags(str(content))
            if len(content) > 500:
                softData.append([])
                linkParts = linksWithSoftware[i].split(':')
                teamName = linkParts[2].split('/')
                try:
                    softData[len(softData) - 1].append(teamName[0])
                except Exception as e:
                    print(e)
                    softData[len(softData) - 1].append('')
                softData[len(softData) - 1].append(content)
            progress.emit(20 / len(linksWithSoftware))
        return softData

if __name__ == '__main__':
    scraper = Scraper()
    scraper.getSoftwareLinks(2008, progress=0)