#!/usr/bin/python
# -*- coding: utf-8 -*-

from scrapy import Selector
from requests import Request, Session
import urlparse
from selenium import webdriver
import os.path
import string
import codecs


work_dir = os.path.dirname(os.path.abspath(__file__))
#print work_dir
ts_file = "/timestamp.txt"
url = "http://clubnika.com.ua/home/"

# Timestamp
old_checkpoint = codecs.open(work_dir+ts_file, encoding="utf-8").read() if os.path.exists(work_dir+ts_file) else ''
new_checkpoint = ''
#print old_checkpoint

s = Session()

header = {}
post_data = {"login": "+380679695627", "password":"8027541", "signin":"Войти"}


req = Request('POST', url,data = post_data, headers=header)

prepped = req.prepare()

prepped.headers["Referer"] = "http://clubnika.com.ua/home/"
prepped.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
prepped.headers["Origin"] = "http://clubnika.com.ua"
prepped.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12"

resp = s.send(prepped)
"""
print resp.cookies['X']
sel=Selector(text=resp.content)

path = sel.xpath("//div[@class='header']//li//a[@class='icon']/@href").extract()[0]
ref = urlparse.urljoin(url, path)
"""
#url_profile = "http://clubnika.com.ua/profile/?id=36657"
#url_tv_chat = "http://clubnika.com.ua/tv-chat"
browser = webdriver.Chrome()
i = 1
s1 = Session()
while(1):
    url_tv_chat = "http://clubnika.com.ua/tv-chat/?action=view&room=1&page=" + str(i)
    req1 = Request('GET', url_tv_chat, cookies=resp.cookies, headers=header)
    prepped1 = req1.prepare()

    prepped1.headers["Referer"] = "http://clubnika.com.ua/guest/"
    prepped1.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    prepped1.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12"
    resp1 = s1.send(prepped1)

    open("/tmp/clubnika.html", "wb").write(resp1.content)
    browser.get("file:///tmp/clubnika.html")
    sel = Selector(text = browser.page_source)
    blocks = sel.xpath("//div[@class='p10']").extract()
    for block in blocks:
        #print block
        sel1 = Selector(text = block)
        name = sel1.xpath('//div[@class="p10"]/b/text()').extract()
        if len(name)==0 or name[0] !=  u'\u041c\u043e\u0434\u0435\u0440':
            msg_body = sel1.xpath("//span[@class='c1']/text()").extract()
            if len(msg_body):
                cur_ts = sel1.xpath("//small/text()").extract()[0]
                msg_body = cur_ts + "," + msg_body[0].replace('\n', ' ').replace('\r', '').replace(',', ' ')
                if new_checkpoint=="":
                    new_checkpoint = msg_body
                    if old_checkpoint=="":
                        open(work_dir+ts_file, "w").write(new_checkpoint.encode("utf8"))
                #print "OLD: ",  type(old_checkpoint), len(old_checkpoint), old_checkpoint
                #print "NEW: ", type(msg_body), len(msg_body), msg_body
                if old_checkpoint.strip('\n') == msg_body.strip('\n'):
                    open(work_dir+ts_file, "w").write(new_checkpoint.encode("utf8"))
                    os._exit(0)
                open(work_dir+"/clubnica.txt", "a").write(msg_body.encode("utf8")+'\n')
    i = i+1