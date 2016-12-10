# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
import json
import codecs

class DcspiderPipeline(object):
    def __init__(self):
        self.file = codecs.open('items.txt', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        if item["description"][0] != '':
            line = item["url"][0] + ' ' + item["name"][0] + ' ' + item["description"][0] + "\n"
        else:
            line=  item["url"][0] + ' ' + item["name"][0] + ' ' + item["name"][0] + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()
