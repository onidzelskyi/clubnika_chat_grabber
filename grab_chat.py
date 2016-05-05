#!/usr/bin/python
# -*- coding: utf-8 -*-

from scrapy import Selector
from requests import Request, Session
import urlparse
from selenium import webdriver
import os.path
import string
import codecs
import sqlite3
import re
import requests
import json
from dateutil import parser
# Start display before Chrome browser
from pyvirtualdisplay import Display
import argparse # Arguments parser
import time # sleep


# Constants
# File name of sqlite database will be stored
DB_FILE_NAME = "clubnika.db"
# File name of message we start to grab last time
TIMESTAMP_FILE = "/timestamp.txt"
# File name of url' page number
DEEP_FILE = "/deep.txt"
# URL of the service we grab for
SERVICE_URL = "http://clubnika.com.ua/home/"
# We start to grab form first page
DEEP_BEGIN = 1
# sql query to create table for storing the data we recieve from the service
SQL_CREATE_QUERY = "CREATE TABLE IF NOT EXISTS messages(timestamp DATE, msg TEXT, phone TEXT, label TEXT)"
EMPTY_CHECKPOINT = ""
# Timeout between GET requests in seconds
TIMEOUT = 1
# Empirical value for phone extraction
MAX_STEP_SIZE = 7
CHECK_PHONE = 1
CLASSIFY = 0


# class Grab
class Grab(object):
    def __init__(self):
        self.work_dir = os.path.dirname(os.path.abspath(__file__))
        self.timestamp_file = TIMESTAMP_FILE
        self.deep_file = DEEP_FILE
        self.url = SERVICE_URL
        self.deep = DEEP_BEGIN
        self.old_checkpoint = EMPTY_CHECKPOINT
        self.new_checkpoint = EMPTY_CHECKPOINT
        self.conn = sqlite3.connect(DB_FILE_NAME)

    def load(self):
        self.parseArgs()
        self.createDB()
        self.loadOldCheckPoint()
        self.loadDeep()
        # Add current path to PATH environment variable for chrome driver
        os.environ["PATH"] += os.pathsep + self.work_dir

    def run(self):
        self.fetchMsg()
    
    def createDB(self):
        with self.conn as cur:
            cur.execute(SQL_CREATE_QUERY)

    def fetchMsg(self):
        # Create session
        s = Session()
        
        # Fill up headers
        header = {}
        post_data = {"login": "+380679695627", "password":"8027541", "signin":"Войти"}
        req = Request('POST', self.url, data = post_data, headers=header)
        prepped = req.prepare()
        prepped.headers["Referer"] = "http://clubnika.com.ua/home/"
        prepped.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        prepped.headers["Origin"] = "http://clubnika.com.ua"
        prepped.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12"
        
        # Make request
        resp = s.send(prepped)
        
        # Run without GUI
        display = Display(visible=0, size=(800, 800))
        display.start()
        browser = webdriver.Chrome()
        
        s1 = Session()
        completed = False
        while(not completed):
            time.sleep(TIMEOUT)
            #print "deep: %d" % self.deep
            batch = []
            url_tv_chat = "http://clubnika.com.ua/tv-chat/?action=view&room=1&page=" + str(self.deep)
            req1 = Request('GET', url_tv_chat, cookies=resp.cookies, headers=header)
            prepped1 = req1.prepare()
            
            prepped1.headers["Referer"] = "http://clubnika.com.ua/guest/"
            prepped1.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            prepped1.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12"
            resp1 = s1.send(prepped1)
            import pdb; pdb.set_trace()
            open("/tmp/clubnika.html", "wb").write(resp1.content)
            browser.get("file:///tmp/clubnika.html")
            sel = Selector(text = browser.page_source)
            blocks = sel.xpath("//div[@class='p10']").extract()
            for block in blocks:
                sel1 = Selector(text = block)
                name = sel1.xpath('//div[@class="p10"]/b/text()').extract()
                if len(name)==0 or name[0] !=  u'\u041c\u043e\u0434\u0435\u0440':
                    msg_body = sel1.xpath("//span[@class='c1']/text()").extract()
                    if len(msg_body) and len(sel1.xpath("//small/text()").extract()):
                        cur_ts = sel1.xpath("//small/text()").extract()[0]
                        msg_body = msg_body[0].replace('\n', ' ').replace('\r', '').replace(',', ' ')
                        check_point = cur_ts + "," + msg_body
                        batch.append((parser.parse(cur_ts), msg_body, '', '',))
                        print(batch)
                        # At the first touch save new checkpoint
                        if self.new_checkpoint==EMPTY_CHECKPOINT: self.new_checkpoint = check_point.strip("\n")
                        
                        #if self.old_checkpoint==EMPTY_CHECKPOINT and self.args.update:
                        if self.old_checkpoint==EMPTY_CHECKPOINT or self.outdated():
                            #print "Outdated"
                            with open(self.work_dir+self.timestamp_file, "w") as f:
                                f.write(self.new_checkpoint.encode("utf8"))
                        #print "%s\n%s\n\n" % (self.old_checkpoint.strip('\n'), check_point.strip('\n'))
                        if self.old_checkpoint.strip('\n') == check_point.strip('\n'):
                            #open(self.work_dir+self.timestamp_file, "w").write(self.new_checkpoint.encode("utf8"))
                            completed = True
                            break
                        if self.old_checkpoint==EMPTY_CHECKPOINT: self.old_checkpoint = self.new_checkpoint
            #os._exit(0)
            if CHECK_PHONE:
                batch = self.checkPhone(batch)
            if CLASSIFY:
                batch = self.classify(batch)
            self.saveEntry(batch)
            
            # next crawling page
            self.deep += 1
        
        # Save current deep
        if self.args.dig: self.saveDeep()

    # load last available checkpoint
    def loadOldCheckPoint(self):
        # Timestamp
        # If the program run in update mode
        # and file with the last timestamp exists
        # then load old checkpoint
        self.old_checkpoint = EMPTY_CHECKPOINT
        if os.path.exists(self.work_dir+self.timestamp_file):
            self.old_checkpoint = codecs.open(self.work_dir+self.timestamp_file, encoding="utf-8").read()

    # load last available deep
    def loadDeep(self):
        if self.args.dig and os.path.exists(self.work_dir+self.deep_file):
            self.deep = long(open(self.work_dir+self.deep_file).read())

    def saveEntry(self, batch):
        with self.conn as cur:
            with open("sample.txt", "wb") as fout:
                fout.write(str(batch))
                fout.write(str(("INSERT INTO messages VALUES(?,?,?,?)",batch)))
                os._exit(0)
            cur.executemany("INSERT INTO messages VALUES(?,?,?,?)",batch)
        #conn.commit()

    # save last available deep
    def saveDeep(self):
        with open(self.work_dir+self.deep_file, "w") as f:
            f.write(str(self.deep))

    # save last available deep
    def outdated(self):
        #print "self.old_checkpoint: ", self.old_checkpoint
        #print "self.new_checkpoint: ", self.new_checkpoint
        return True if self.args.update and self.old_checkpoint!=self.new_checkpoint else False
    
    ##
    # Argument parser
    #
    def parseArgs(self):
        parser = argparse.ArgumentParser(description="Parse image files.")
        parser.add_argument("-u", "--update", action="store_true", help = "update by the new messages")
        parser.add_argument("-d", "--dig", action="store_true", help = "continue form stop point")
        self.args = parser.parse_args()
        # if neither flags set
        # or set both of them
        # Exit
        if (not self.args.update and not self.args.dig) or (self.args.update and self.args.dig) :
            raise Exception("Please, set one from update or dig.")




    def checkPhone(self, batch):
        new_batch = []
        for entry in batch:
            # Omit digits in unicode format
            str = unicode(entry[1]).replace(u'\u0417', "3")
            
            # Leave only numbers in string
            str = re.sub("[^0-9]", " ", str)

            i = 0
            phone = ""
            phones = []
            for c in str:
                if c.isdigit():
                    if i<MAX_STEP_SIZE:
                        i = 0
                        phone = phone + c
                    elif len(phone):
                        phones.append(phone)
                        phone = c
                        i = 0
                elif len(phone):
                    i = i+1

            if len(phone):
                phones.append(phone)
            
            lst = list(entry)
            a = [phone for phone in phones if len(phone)>8]
            lst[2] = a[0] if len(a) else ""
            new_batch.append(tuple(lst))
        return new_batch


def classify(batch):
    text_list = [x[1] for x in batch]
    data = {
        'text_list': text_list
    }
    response = requests.post(
                             "https://api.monkeylearn.com/v2/classifiers/cl_VL7oNpx2/classify/?sandbox=1",
                             data=json.dumps(data),
                             headers={'Authorization': 'Token 423b24aece62d16fc58e62de1490eeb06db2d80f',
                             'Content-Type': 'application/json'})
    labels = json.loads(response.text)["result"]
    new_batch = []
    for i,x in enumerate(batch):
        new_batch.append((batch[i][0], batch[i][1], batch[i][2], labels[i][0]["label"]))
    return new_batch


def main():
    # Parse arguments
    # args.update
    # args.dig
    grab = Grab()
    try:
        grab.load()
        grab.run()
    except Exception as e:
        print e
    finally:
        if grab.args.dig: grab.saveDeep()



if __name__ == "__main__":
    main()
