import json
import csv
import requests
import time
from simhash import Simhash
from bs4 import BeautifulSoup
from googleapiclient.discovery import build

my_api_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
my_cse_id = "xxxxxxxxx"

corpus_dict = {}
gquery_dict = {}
mapped = {}
greq_time = 0

def disambiguation(link):
    k = []
    if link not in corpus_dict.keys():
        corpus_dict[link] = requests.get(link).content
    soup = BeautifulSoup(corpus_dict[link], 'html.parser', from_encoding="utf-8")
    result = soup.find("div", id="mw-normal-catlinks")
    if result == None:
        return True
    results = result.select("li")
    for a in results:
        name = a.select_one('a')
        if 'ambiguation' in name['href'] or 'Lists' in name['href'] or 'lists' in name['href']:
            return False
    return True

def google(search_term, api_key, cse_id, **kwargs):
    global greq_time
    greq_time = greq_time + 1
    print(greq_time)
    service = build("customsearch", "v1", developerKey=my_api_key)
    results = service.cse().list(q=search_term, cx=my_cse_id, **kwargs).execute()
    res = []
    if 'items' in results.keys():
        for i in results['items'][:1]:
            if disambiguation(i['link']) == True:
                res.append(i['link'])
    return res

# search with google
def cloest_topic(base_topic, base_url, query):
    # get corpus on nist
    if base_url not in corpus_dict.keys():
        corpus_dict[base_url] = requests.get(base_url).content
    base_corpus = BeautifulSoup(corpus_dict[base_url], 'html.parser').get_text()
    # key: value = link: similarity
    sim_res = {}
    if query not in gquery_dict.keys():
        gquery_dict[query] = google(query, my_api_key, my_cse_id)
    results = gquery_dict[query]
    if len(results) == 0:
        return '', 100000000
    try:
        for cmp_link in results:
            if cmp_link not in corpus_dict.keys():
                corpus_dict[cmp_link] = requests.get(cmp_link).content
            cmp_corpus = BeautifulSoup(corpus_dict[cmp_link], 'html.parser').get_text()
            res = Simhash(base_corpus).distance(Simhash(cmp_corpus))
            sim_res[cmp_link] = res
    except:
        sim_res = {}
    if len(sim_res) == 0:
        return '', 100000000
    cloest_link = min(sim_res.items(), key = lambda x: x[1])[0]
    cloest_dist = sim_res[cloest_link]
    return cloest_link, cloest_dist

def cloest_keyword(base_topic, base_url):
    ld = {}
    query = base_topic + ' data structure'
    link1, dist1 = cloest_topic(base_topic, base_url, query)
    ld[link1] = dist1
    query = base_topic + ' algorithm'
    link2, dist2 = cloest_topic(base_topic, base_url, query)
    ld[link2] = dist2
    min_link = min(ld.items(), key = lambda x: x[1])
    if dist1 == 100000000 and dist2 == 100000000:
        print(base_topic + ' should be removed!')
        return ''
    return min_link[0]
        
def get_corpus(row):
    concept = json.loads(row)
    kg = concept['knowledge']
    if kg in mapped.keys():
        return mapped[kg], BeautifulSoup(corpus_dict[mapped[kg]], 'html.parser').get_text()
    print(kg)
    link = concept['link']
    kw_link = cloest_keyword(kg, link)
    if kw_link == '':
        with open('./mapped.txt', 'a+') as output:
            res = kg + ' ' + 'no' + '\n'
            output.write(res)
        output.close()
        return kw_link, ''
    mapped[kg] = kw_link
    if kw_link not in corpus_dict.keys():
        corpus_dict[kw_link] = requests.get(kw_link).content
    corpus = BeautifulSoup(corpus_dict[kw_link], 'html.parser').get_text()
    with open('./mapped.txt', 'a+') as output:
        res = kg + ' ' + kw_link + '\n'
        output.write(res)
    output.close()
    return kw_link, corpus

def main():
    res = []
    count = 0
    with open('../dataset/concept_pair.csv', 'r') as concept_pair:
        csv_reader = csv.reader(concept_pair, delimiter=',')
        for row in csv_reader:
            count = count + 1
            if count > 1:
                r = []
                link1, corpus1 = get_corpus(row[0])
                time.sleep(1)
                if corpus1 == '':
                    continue
                link2, corpus2 = get_corpus(row[1])
                time.sleep(1)
                if corpus2 == '':
                    continue
                # get the similarity distance between two corpus
                #sim_distance = Simhash(corpus1).distance(Simhash(corpus2))
                #r.append(sim_distance)
                #res.append(r)
    concept_pair.close()
    print(len(res))
    print(res)

main()
