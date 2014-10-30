# -*- coding: utf-8 -*-
from scrapy.spider import BaseSpider
from spider.items import *
from scrapy.selector import Selector
from scrapy.http.request import Request
from hashlib import md5
import random
import time

class DoubanTop250(BaseSpider):
    name            = "douban.top250"
    allowed_domains = ["douban.com"]
    start_urls      = ["http://movie.douban.com/top250?start=0&filter=&type="]
    index           = 0
    movie_urls      = []
    
    def parse_movie(self, response):
        sel   = Selector( response )
        movie = MovieItem()
        movie["name"]       = sel.xpath("//div[@id='content']/h1/span[1]/text()").extract()[0]
        movie["dna"]        = md5( movie["name"].encode("utf-8") ).hexdigest()
        movie["director"]  = sel.xpath("//div[@id='info']/span[1]/a/text()").extract()[0]
        movie["actor"]      = u",".join(sel.xpath("//div[@id='info']/span[3]/a/text()").extract())
        t                    = response.xpath("//div[@id='info']/text()").extract()
        info                 = [ i.strip() for i in t if len(i.strip())>1 ]
        movie["country"]   = info[0]
        movie["alias"]      = info[2]
        movie["show_time"]  = u",".join(sel.xpath("//div[@id='info']/span[@property='v:initialReleaseDate']/text()").extract())
        movie["brief"]      = sel.xpath("//div[@class='related-info']/div[1]/span/text()").extract()[0].strip()
        movie["url"]        = response.url
        
        print movie["name"]
        
        return movie
    
    def parse(self, response):
        sel   = Selector( response )
        href  = sel.xpath("//div[@class='pic']/a/@href").extract()
        if len(href):
            self.movie_urls.extend(href)
            
        if self.index<250:
            self.index += 25
            yield Request("http://movie.douban.com/top250?start=%d&filter=&type="%(self.index), callback=self.parse)
        else:
            for url in self.movie_urls:
                yield Request(url, callback=self.parse_movie)
        
        