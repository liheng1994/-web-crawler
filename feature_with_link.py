import requests
from bs4 import BeautifulSoup
import difflib
import numpy as np
web='https://xlinux.nist.gov/dads/HTML/gnomeSort.html'
web2='https://xlinux.nist.gov/dads/HTML/insertionSort.html'
content1=requests.get(web)
content1.text
content2=requests.get(web2)
content2.text
li1=[]
li2=[]
soup1=BeautifulSoup(content1.text,"html.parser")
soup2=BeautifulSoup(content2.text,"html.parser")
for links in soup1.find_all('p'):
    for section in links.find_all('strong'):
        if section.text=='Definition:'or section.text=='Also known as' or section.text=='Generalization' or section.text=='Specialization' or section.text=='Aggregate parent' or section.text=='See also':
            link1=links.select('a em')
            for name in link1:
                li1.append(name.text)
        else:
            break
for links in soup2.find_all('p'):
    for section in links.find_all('strong'):
        if section.text=='Definition:'or section.text=='Also known as' or section.text=='Generalization' or section.text=='Specialization' or section.text=='Aggregate parent' or section.text=='See also':
            link2=links.select('a em')
            for name in link2:
                li2.append(name.text)
        #    li2.append(links.select('a em').text)
        else:
            break
print(li1)
print(li2)
print(difflib.SequenceMatcher(None,li1,li2).ratio())

#        print(section.text)
#    if links.find('strong')!=None and links.find('a')==None:
#        li1+=links.find('strong')
#        li2+=links.find('a')

#print(li1)
#print(li2)