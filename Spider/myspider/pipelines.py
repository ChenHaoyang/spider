# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import csv
from myspider import settings
import MeCab as mc


def write_to_csv(item):
    writer = csv.writer(open(settings.CSV_FILE_PATH, 'a'), lineterminator='\n')
    writer.writerow([item['content']])
    #writer.writerow([item[key] for key in item.keys()])
    
class MyspiderPipeline(object):
    tagger=mc.Tagger('-Ochasen -d /usr/lib/mecab/dic/mecab-ipadic-neologd/')
     
    def process_item(self, item, spider):
        if item['id'] == None:
            return item
        keywords = []
        tmp = item['content']
        node = self.tagger.parseToNode(tmp).next
        while node:
            if node.feature.split(",")[0]=="名詞" or node.feature.split(",")[0]=="形容詞" or node.feature.split(",")[0]=="動詞":
                if node.feature.split(",")[1]!="非自立":
                    keywords.append(node.surface)
            node=node.next
        s=""
        for w in keywords:
            s+=w+" "
        item['content']= s.strip()
        write_to_csv(item)
        return item
