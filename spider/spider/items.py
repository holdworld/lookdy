# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

class MovieItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    dna        = Field()
    name       = Field()
    alias      = Field()
    time       = Field()
    director   = Field()
    actor      = Field()
    country    = Field()
    type       = Field()
    url        = Field()
    brief      = Field()

