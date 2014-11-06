# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb.connections

class MoviePipeline(object):
    def __init__(self):
        self.cnx=MySQLdb.connect("127.0.0.1", "root", "", "lookdy")
        self.cnx.set_character_set("utf8")
        self.movie_sql=("INSERT movie VALUE(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
        self.play_sql=("INSERT play VALUE(%s,%s,%s,%s)")

    def process_item(self, item, spider):
        cursor=self.cnx.cursor()

        try:
            print(item['actor'])
            cursor.execute( self.movie_sql, (item['dna'],item['name'],item['alias'],item['time'],item['director'],
                                             item['actor'],item['country'],item['type'],item['url'],item['brief']) )
            self.cnx.commit()
        except:
            print( item['url'] )

        cursor.close()

class SpiderPipeline(object):
    def process_item(self, item, spider):
        return item
