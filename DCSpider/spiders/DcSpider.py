# -*- coding:utf-8 -*-
import scrapy
from scrapy.selector import Selector
from DCSpider.items import DcspiderItem
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import Rule
from urlparse import urljoin
import json
import codecs
import re
from scrapy.contrib.loader import ItemLoader
class DCSpider(scrapy.Spider):
    name='dcw'
    start_urls=["http://mycd.qq.com/f-1001252491-1.htm",]
    # rules = (
    #     # 将所有符合正则表达式的url加入到抓取列表中
    #     Rule(SgmlLinkExtractor(allow=(r'http://mycd\.qq\.com/f-1001252491-\d+',)),callback='parse_page', follow=True),
    #     # 将所有符合正则表达式的url请求后下载网页代码, 形成response后调用自定义回调函数
    #     # Rule(SgmlLinkExtractor(allow=(r'http://mycd\.qq\.com/\t.+',)),
    #     #      callback='parse_page', follow=True),
    # )
    base_url='http://mycd.qq.com'
    # codecs.open('items.json', 'w', encoding='utf-8').close()
    # def parse(self, response):
    #     sel = Selector(response)
    #     sites = sel.xpath('//th/a[@href != "javascript:;"]')
    #     nxtpage_url=sel.xpath('//div[@class="page_box y"]/div/a[@class="nxt"]/@href').extract()
    #     items = []
    #     for site in sites:
    #         item =DcspiderItem()
    #         item['name'] = site.xpath('text()').extract()
    #         item['url'] = site.xpath('@href').extract()
    #         # item['description'] = site.xpath('text()').re('-\s[^\n]*\\r')
    #         f= codecs.open('items.json', 'a', encoding='utf-8')
    #         line = json.dumps(dict(item), ensure_ascii=False) + "\n"
    #         f.write(line)
    #         f.close()
    #     try:
    #         if nxtpage_url[0]:
    #             request = scrapy.Request(urljoin(self.base_url, nxtpage_url[0]), callback=self.parse)
    #             yield request
    #     except:
    #         pass


    def parse(self, response):
        sel = Selector(response)
        article_url = sel.xpath('//th/a[@href != "javascript:;"]/@href').extract()
        nxtpage_url = sel.xpath('//div[@class="page_box y"]/div/a[@class="nxt"]/@href').extract()
        item = DcspiderItem()
        # for site in sites:
        #     item = DcspiderItem()
        #     item['name'] = site.xpath('text()').extract()
        #     item['url'] = site.xpath('@href').extract()
        #     # item['description'] = site.xpath('text()').re('-\s[^\n]*\\r')
        #     f = codecs.open('items.json', 'a', encoding='utf-8')
        #     line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        #     f.write(line)
        #     f.close()
        for url in article_url:
            urll = urljoin(self.base_url, url)
            # 调用parse_item解析文章内容
            request = scrapy.Request(urll, callback=self.parse_item)
            request.meta['item'] = item
            yield request
        try:
            if nxtpage_url[0]:
                request = scrapy.Request(urljoin(self.base_url, nxtpage_url[0]), callback=self.parse)
                yield request
        except:
            pass

    def parse_item(self,response):
        #还存在有一条帖子有多页回复的情况，此处暂不处理
        content = u''
        sel = Selector(response)
        item = response.meta['item']
        l = ItemLoader(item=DcspiderItem(), response=response)
        article_url=str(response.url)
        article_name=sel.xpath('//h1/a[@id="thread_subject"]/text()').extract()
        article_description=sel.xpath('//div[@class="wp cl mtl"]/div[@class="w865 z"]/div[@id="postlist"]'
                                      '//div[@id != "postlistreply"]')
                                      # '/table[@class="plhin"]'
                                      # '/tr'
                                      # '/td[not(@class)]'
                                      # '/div[@class="pct ptm"]/'
                                      # 'div/div[@class="t_fsz"]/table/tr/td[@class="t_f"]/text()'
                                      # ).extract()
        #经观察，每篇的帖子的第一部分第一部分div为正文，此后为评论
        description=[]
        for des in article_description:
            post_article = des.xpath('table[@class="plhin"]/tr/td[not(@class)]/div[@class="pct ptm"]/'
                                      'div/div[@class="t_fsz"]/table/tr/td[@class="t_f"]/text()|'
                                    'table[@class="plhin"]/tr/td[not(@class)]/div[@class="pct ptm"]/'
                                      'div/div[@class="t_fsz"]/table/tr/td[@class="t_f"]/font/font/text()|'
                                    'table[@class="plhin"]/tr/td[not(@class)]/div[@class="pct ptm"]/'
                                      'div/div[@class="t_fsz"]/table/tr/td[@class="t_f"]/div/text()|'
                                    'table[@class="plhin"]/tr/td[not(@class)]/div[@class="pct ptm"]/'
                                      'div/div[@class="t_fsz"]/table/tr/td[@class="t_f"]/div/font/text()|'
                                    'table[@class="plhin"]/tr/td[not(@class)]/div[@class="pct ptm"]/'
                                      'div/div[@class="t_fsz"]/table/tr/td[@class="t_f"]/font/font/font/text()|'
                                    'table[@class="plhin"]/tr/td[not(@class)]/div[@class="pct ptm"]/'
                                      'div/div[@class="t_fsz"]/table/tr/td[@class="t_f"]/font/font/font/font/text()'
                                    ).extract()

            for article in post_article:
                content=content+article
            if content == ''or content == '\r\n'or content=='\r\n\r\n':pass
            else:
                content=content.replace(u'\r','').replace(u'\n','').replace(u' ','')
                content=re.sub(u'[\u3000,\xa0]',u'',content)
                description.append(content)
            content=u''
        article_name[0] = re.sub(u'[\u3000,\xa0]',u'',article_name[0])
        article_name=article_name[0].replace(u' ','')
        article_url = article_url
        article_description = description
        print article_name, article_url
        l.add_value('name', article_name)
        l.add_value('url', article_url)
        l.add_value('description', article_description)
        yield l.load_item()


