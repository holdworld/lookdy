# -*- coding: utf-8 -*-
from scrapy.spider import BaseSpider
from spider.items import *
from scrapy.selector import Selector
from scrapy.http.request import Request
from hashlib import md5
import random
import time

class DoubanMovie(BaseSpider):
    '''douban movie spider, usage:
       scrapy crawl douban.movie -a surl=start_url -a idx="parse_page|parse_movie"

       example:
              scrapy crawl douban.movie -a surl="http://movie.douban.com/top250"
              scrapy crawl douban.movie -a surl="http://movie.douban.com/subject/1292052/" -a idx="parse_movie"
    '''
    name            = "douban.movie"
    start_urls      = []
    index           = 0
    movie_urls      = []
    parse_idx       = ""
    parse_fun       = {}

    def __init__(self, surl=None, idx="parse_page"):
        self.start_urls.append(surl)
        self.parse_idx  = idx
        self.parse_fun  = {"parse_movie":self.parse_movie,
                           "parse_page":self.parse_page}

    def start_requests(self):
        print("start request.", self.parse_idx)

        yield Request( self.start_urls[0], callback=self.parse_fun[self.parse_idx] )

    def parse_movie(self, response):
        if response.status != 200:
            return

        sel   = Selector( response )
        movie = MovieItem()

        movie["name"]       = sel.xpath("//div[@id='content']/h1/span[1]/text()").extract()[0]
        movie["dna"]        = md5( movie["name"].encode("utf-8") ).hexdigest().decode("utf-8")
        movie["type"]       = sel.xpath("//div[@id='info']/span[@property='v:genre']/text()").extract()[0]
        movie["director"]  = sel.xpath("//div[@id='info']/span[1]/a/text()").extract()[0]
        movie["actor"]      = u",".join(sel.xpath("//div[@id='info']/span[3]/a/text()").extract())

        t                    = response.xpath("//div[@id='info']/text()").extract()
        info                 = [ i.strip() for i in t if len(i.strip())>1 ]
        try:
            movie["country"]  = info[0]
            movie["alias"]    = info[2]
        except:
            pass

        movie["time"]    = u",".join(sel.xpath("//div[@id='info']/span[@property='v:initialReleaseDate']/text()").extract())
        movie["url"]     = response.url.decode('utf-8')

        summaries    = sel.xpath("//span[@property='v:summary']/text()").extract()
        movie["brief"] = summaries[0].strip()
        for summary in summaries[1:]:
            movie["brief"] = movie["brief"] + u"\n" + summary.strip()

        try:
            print movie["name"]
        except:
            pass

        return movie

    def parse_page(self, response):
        print(response.url)

        sel   = Selector( response )
        href  = sel.xpath("//div[@class='pic']/a/@href").extract()
        if len(href):
            self.movie_urls.extend(href)

        try:
            next_page = sel.xpath( "//span[@class='next']/a/@href" ).extract()[0]
            yield Request( self.start_urls[0]+next_page, callback=self.parse_page )
        except:
            for url in self.movie_urls:
                yield Request( url, callback=self.parse_movie )
