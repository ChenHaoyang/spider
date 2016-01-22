# coding: utf-8

from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider,Rule
import urllib2
from bs4 import BeautifulSoup

from myspider.items import MyspiderItem
from myspider import settings
#from bs4 import BeautifulSoup
import re
from pyasn1.compat.octets import null
from urllib2 import urlopen

class MySpider(CrawlSpider):
    name = "myspider"
    allowed_domains = ["news.yahoo.co.jp",
                       "headlines.yahoo.co.jp",
                       "zasshi.news.yahoo.co.jp"]
    #start_urls = [
    #    "http://www.dmoz.org/Computers/Programming/Languages/Python/Books/",
    #    "http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/"
    #]
    start_urls = [url.strip() for url in open(settings.URL_FILE_PATH)]
    rules=(
           Rule(LinkExtractor(allow=r"/hl.*"), callback="parse_news"),
           Rule(LinkExtractor(allow=r"/article\?a=.*", deny=r"/.*\.view-000"), callback="parse_news"),
           Rule(LinkExtractor(allow=r"/pickup/\d+"), callback="parse_news",follow=True),
           Rule(SgmlLinkExtractor(restrict_xpaths=("//a[@class='next']")), callback='parse_news', follow=True),
           Rule(SgmlLinkExtractor(restrict_xpaths=("//a[@class='newsLink']")), callback='parse_news'),
           )
    count = 1

    def parse_news(self, response):
        item = MyspiderItem()
        #tmp=response.xpath("//div[@class='headlineTxt']/h2[@class='newsTitle']/a/text()|//div[@class='headlineTxt']/p[@class='hbody']/text()").extract()
        tmp = response.xpath("//p[@class='ynDetailText']/text()").extract()
        if len(tmp) == 0:
            tmp=response.xpath("//a[@class='newsLink']/text()").extract()
            if len(tmp)>0:
                if tmp[0] == u"[記事全文]":
                    return item
                else:
                    tmp=response.xpath("//div[@class='headlineTxt']/h2[@class='newsTitle']/a/text()|//div[@class='headlineTxt']/p[@class='hbody']/text()").extract()
            else:
                return item
        
        word_str=""
        s=""
        for w in tmp:
            s+=w.encode("utf-8")
        #word_list = re.findall(u"[\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF\n ]+",response.body_as_unicode(),re.U)
        
        url = response.xpath("//li[@class='next']/a/@href").extract()
        if len(url)>0:
            while url[0] != None:
                html = urlopen(url[0])
                soup = BeautifulSoup(html)
                s += soup.find('p',class_='ynDetailText').text.encode("utf-8")
                temp_soup = soup.find('li', class_='next').find('a')
                if temp_soup != None:
                    url[0]=temp_soup['href'].encode("utf-8")
                else:
                    url[0]=None
                
        for w in re.findall(u"[\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF]+",s.decode("utf-8"),re.U):
           word_str+=w
        #lines=(line.strip() for line in s.splitlines())
        #chunks=(phrase.strip() for line in lines for phrase in line.split(" "))
        #s='\n'.join(line for line in lines if line)
        item['id'] = self.count
        item['content'] = word_str.encode('utf-8')
        self.count = self.count +1
        
        return item
    
        
        
        
    #88830