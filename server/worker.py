#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2012, Grant Drake <grant.drake@gmail.com>'
__docformat__ = 'restructuredtext en'

import json, socket, re, datetime
from threading import Thread

from lxml.html import fromstring, tostring

from models import ItemsMelon
from models import ItemsDLSite
from models import ItemsFanza

class WorkerCommon(Thread):

    def __init__(self, browser, url, search_item, relevance, result_queue, timeout):
        Thread.__init__(self)
        self.daemon = True
        self.browser = browser.clone_browser()
        self.url = url
        self.search_item = search_item
        self.relevance = relevance
        self.result_queue = result_queue
        self.timeout = timeout

        self.ID = ""
        self.title = ""
        self.authors = []
#       self.isbn = ""
        self.comments = ""
        self.cover_url = ""
        self.has_cover = False
        self.tags = []
        self.gunre = ""
        self.monopoly = False
        self.pubdate = ""
        self.publisher = ""
        self.event = ""

    def createRecord(self, itemsClass):
        authname = ""
        for authIdx, authElem in enumerate(self.authors):
            if(authIdx != 0):
                authname = authname + ' & '
            authname = authname + authElem

        tagname = ""
        for tagIdx, tagElem in enumerate(self.tags):
            if(tagIdx != 0):
                tagname = tagname + ', '
            tagname = tagname + tagElem

        pubdateF = ""
        if self.pubdate:
            pubdateF = datetime.datetime.strptime(self.pubdate, "%Y/%m/%d").date()

        record = itemsClass(
            item_id = self.ID,
            title = self.title,
            authors = authname,
            comments = self.comments,
            cover_url = self.cover_url,
            has_cover = self.has_cover,
            tags = tagname,
            gunre = self.gunre,
            monopoly = self.monopoly,
            pubdate = pubdateF,
            publisher = self.publisher,
            event = self.event,
        )
        return record

    def printMetadata(self):
        authname = ""
        for authIdx, authElem in enumerate(self.authors):
            if(authIdx != 0):
                authname = authname + ' & '
            authname = authname + authElem

        tagname = ""
        for tagIdx, tagElem in enumerate(self.tags):
            if(tagIdx != 0):
                tagname = tagname + ', '
            tagname = tagname + tagElem

        print("")
        print("*********************************************************")
        print("     SEQ : " + str(self.relevance))
        print("      ID : " + self.ID)
        print("   TITLE : " + self.title)
        print(" AUTHORS : " + authname)
#       self.isbn = ""
        print(" COMMENT : " + self.comments)
        print("    TAGS : " + tagname)
        print("   GUNRE : " + self.gunre)
        print("  SENBAI : " + str(self.monopoly))
        print(" PUBDATE : " + self.pubdate)
        print(" PUBLISH : " + self.publisher)
        print("     URL : " + self.url)
        print("   COVER : " + self.cover_url)
        print("   EVENT : " + self.event)
        print("*********************************************************")


class WorkerFanza(WorkerCommon): # Get details

    '''
    Get book details from Fanza book page in a separate thread
    '''

    def __init__(self, browser, url, search_item, relevance, result_queue, timeout=40):
        super(WorkerFanza, self).__init__(browser, url, search_item, relevance, result_queue, timeout)

    def createRecord(self):
        record = super(WorkerFanza, self).createRecord(ItemsFanza)
        return record

    def run(self):
        try:
            self.get_details()
        except Exception as e:
            print('get_details failed for url: %r'%self.url)
            print(e)

    def get_details(self):
        try:
            print('Fanza book url: %r'%self.url)
            raw = self.browser.open_novisit(self.url, timeout=self.timeout).read().strip()
        except Exception as e:
            if e.getcode() == 404:
                print('URL malformed: %r'%self.url)
                return
            attr = getattr(e, 'args', [None])
            attr = attr if attr else [None]
            if isinstance(attr[0], socket.timeout):
                msg = 'Fanza timed out. Try again later.'
                print(msg)
            else:
                msg = 'Failed to make details query: %r'%self.url
                print(msg)
            return

        raw = raw.decode('utf-8', errors='replace')

        if '<title>404 - ' in raw:
            print('URL malformed: %r'%self.url)
            return

        try:
            root = fromstring(raw)
        except:
            msg = 'Failed to parse Fanza details page: %r'%self.url
            print(msg)
            return

        self.parse_details( root, self.search_item )

    def parse_details(self, root, search_item):

        try:
            self.ID = self.parse_id(self.url)
        except:
            print('Error parsing Fanza id for url: %r'%self.url)
            self.ID = ""

        try:
            self.title = self.parse_title(root)
        except:
            print('Error parsing title for url: %r'%self.url)
            self.title = ""

        try:
            self.authors = self.parse_authors(root)
        except:
            print('Error parsing authors for url: %r'%self.url)
            self.authors = []

        if not self.title or not self.ID:
            print('Could not find title/dlsite id for %r'%self.url)
            print('Fanza: %r Title: %r'%(self.ID, self.title))
            return

        try:
            self.comments = self.parse_comments(root)
        except:
            print('Error parsing comments for url: %r'%self.url)
            self.comments = ""

        try:
            self.cover_url = self.parse_cover(root)
            # print('INFO cover for: %r'%self.cover_url)
        except:
            print('Error parsing cover for url: %r'%self.url)
            self.cover_url = ""

        self.has_cover = bool(self.cover_url)

        try:
            self.tags = self.parse_tags(root)
        except:
            print('Error parsing tags for url: %r'%self.url)
            self.tags = []

        try:
            self.gunre = self.parse_gunre(root)
        except:
            print('Error parsing gunre for url: %r'%self.url)
            self.gunre = ""

        try:
            self.monopoly = self.parse_monopoly(root)
        except:
            print('Error parsing monopoly for url: %r'%self.url)
            self.monopoly = ""

        try:
            self.pubdate = self.parse_publish_date(root)
            # print('INFO pubdate for: %r'%self.pubdate)
        except:
            print('Error parsing publish date for url: %r'%self.url)
            self.pubdate = ""

        try:
            self.publisher = self.parse_publisher(root)
        except:
            print('Error parsing publisher for url: %r'%self.url)
            self.publisher = ""

        try:
            self.event = self.parse_event(root)
        except:
            print('Error parsing event for url: %r'%self.url)
            self.event = ""

        self.result_queue.append( self )

    def parse_id(self, url):
        return re.search('/dc/doujin/-/detail/=/cid=(.*)/', url).groups(0)[0]

    def parse_title(self, root):
        title_nodes = root.xpath('//meta[@property="og:title"]/@content')
        if title_nodes:
            return title_nodes[0].strip()
        return ""

    def parse_authors(self, root):
        authors_nodes = ""
        # authors_nodes = root.xpath('//*[@id="description"]/table//th[contains(text(), "作家名")]/following-sibling::td/a')
        #
        # if authors_nodes:
        #     tmp_authors_array = []
        #     for i, node in enumerate( authors_nodes, 0 ):
        #         tmp_authors_array.append( node.text_content().strip() )
        #     return tmp_authors_array
        #
        # return self.parse_publisher(root)
        return ""

    def parse_comments(self, root):
        # description_node = root.xpath('//*[@id="description"]/table//th[contains(text(), "イベント")]/following-sibling::td/a')
        # if description_node:
        #     comments = tostring(description_node[0], method='text',encoding=unicode).strip()
        #     while comments.find('  ') >= 0:
        #         comments = comments.replace('  ',' ')
        #     # Since sanitize strips out line breaks, we will leave this commented out for now...
        #     #comments = sanitize_comments_html(comments)
        #     return comments
        return ""

    def parse_cover(self, root):
        imgcol_node = root.xpath('//li[@class="productPreview__item"]//img/@src')
        if imgcol_node:
            img_url = imgcol_node[0].strip()
            return img_url
        return ""

    def parse_gunre(self, root):
        gunre_nodes = root.xpath('//ul[@class="productAttribute-list"]//span[contains(@class,"c_icon_productGenre")]')
        if gunre_nodes:
            return gunre_nodes[0].text_content().strip()
        return ""

    def parse_monopoly(self, root):
        monopoly_nodes = root.xpath('//ul[@class="productAttribute-list"]//span[contains(text(),"専売")]')
        if monopoly_nodes:
            return True
        return False

    def parse_publish_date(self, root):
        pub_date_node = root.xpath('//div[@class="productInformation__item"]//dt[contains(text(), "配信開始日")]/following-sibling::dd')
        if pub_date_node:
            pub_date_text = pub_date_node[0].text_content().strip()

            if pub_date_text[0] == '2':
                pub_date_text = pub_date_text.replace('年', '/').replace('月', '/').replace('日', '')[:10]
                return pub_date_text
        return ""

    def parse_publisher(self, root):
        publisher_nodes = root.xpath('//div[@class="circleName"]//a[@class="circleName__txt"]')
        if publisher_nodes:
            return publisher_nodes[0].text_content().strip()
        return ""

    # UNUSE
    def parse_publisher_url(self, root):
        publisher_urls = root.xpath('//div[@class="circleName"]//a[@class="circleName__txt"]/@href')
        if publisher_urls:
            return publisher_urls[0].strip()
        return ""

    def parse_tags(self, root):
        tag_list = list()
        tag_nodes = root.xpath('//ul[@class="genreTagList"]//li//a')
        if tag_nodes:
            tag_list = [ tag_node.text_content().strip() for tag_node in tag_nodes ]
            return tag_list
        return tag_list

    def parse_event(self, root):
        event_node = root.xpath('//*[@id="work_outline"]//th[contains(text(), "イベント")]/following-sibling::td//a')
        if event_node:
            return event_node[0].text_content().strip()
        return ""

class WorkerDLSite(WorkerCommon): # Get details

    '''
    Get book details from Melonbooks book page in a separate thread
    '''

    def __init__(self, browser, url, search_item, relevance, result_queue, timeout=40):
        super(WorkerDLSite, self).__init__(browser, url, search_item, relevance, result_queue, timeout)

    def createRecord(self):
        record = super(WorkerDLSite, self).createRecord(ItemsDLSite)
        return record

    def run(self):
        try:
            self.get_details()
        except Exception as e:
            print('get_details failed for url: %r'%self.url)
            print(e)

    def get_details(self):
        try:
            print('Dlsite book url: %r'%self.url)
            self.browser.set_simple_cookie('AUTH_ADULT','1','www.melonbooks.co.jp')
            raw = self.browser.open_novisit(self.url, timeout=self.timeout).read().strip()
        except Exception as e:
            if e.getcode() == 404:
                print('URL malformed: %r'%self.url)
                return
            attr = getattr(e, 'args', [None])
            attr = attr if attr else [None]
            if isinstance(attr[0], socket.timeout):
                msg = 'Dlsite timed out. Try again later.'
                print(msg)
            else:
                msg = 'Failed to make details query: %r'%self.url
                print(msg)
            return

        raw = raw.decode('utf-8', errors='replace')

        if '<title>404 - ' in raw:
            print('URL malformed: %r'%self.url)
            return

        try:
            root = fromstring(raw)
        except:
            msg = 'Failed to parse dlsite details page: %r'%self.url
            print(msg)
            return

        self.parse_details( root, self.search_item )

    def parse_details(self, root, search_item):

        try:
            self.ID = self.parse_id(self.url)
        except:
            print('Error parsing dlsite id for url: %r'%self.url)
            self.ID = ""

        try:
            self.title = self.parse_title(root)
        except:
            print('Error parsing title for url: %r'%self.url)
            self.title = ""

        try:
            self.authors = self.parse_authors(root)
        except:
            print('Error parsing authors for url: %r'%self.url)
            self.authors = []

        if not self.title or not self.ID:
            print('Could not find title/dlsite id for %r'%self.url)
            print('Melonbooks: %r Title: %r'%(self.ID, self.title))
            return

        try:
            self.comments = self.parse_comments(root)
        except:
            print('Error parsing comments for url: %r'%self.url)
            self.comments = ""

        try:
            self.cover_url = self.parse_cover(root)
            # print('INFO cover for: %r'%self.cover_url)
        except:
            print('Error parsing cover for url: %r'%self.url)
            self.cover_url = ""

        self.has_cover = bool(self.cover_url)

        try:
            self.tags = self.parse_tags(root)
        except:
            print('Error parsing tags for url: %r'%self.url)
            self.tags = []

        try:
            self.gunre = self.parse_gunre(root)
        except:
            print('Error parsing gunre for url: %r'%self.url)
            self.gunre = ""

        try:
            self.monopoly = self.parse_monopoly(root)
        except:
            print('Error parsing monopoly for url: %r'%self.url)
            self.monopoly = ""

        try:
            self.pubdate = self.parse_publish_date(root)
            # print('INFO pubdate for: %r'%self.pubdate)
        except:
            print('Error parsing publish date for url: %r'%self.url)
            self.pubdate = ""

        try:
            self.publisher = self.parse_publisher(root)
        except:
            print('Error parsing publisher for url: %r'%self.url)
            self.publisher = ""

        try:
            self.event = self.parse_event(root)
        except:
            print('Error parsing event for url: %r'%self.url)
            self.event = ""

        self.result_queue.append( self )

    def parse_id(self, url):
        return re.search('/maniax/work/=/product_id/(.*)\.html', url).groups(0)[0]

    def parse_title(self, root):
        title_nodes = root.xpath('//h1[@id="work_name"]')
        if title_nodes:
            return title_nodes[0].text_content().strip()
        return ""

    def parse_authors(self, root):
        authors_nodes = ""
        # authors_nodes = root.xpath('//*[@id="description"]/table//th[contains(text(), "作家名")]/following-sibling::td/a')
        #
        # if authors_nodes:
        #     tmp_authors_array = []
        #     for i, node in enumerate( authors_nodes, 0 ):
        #         tmp_authors_array.append( node.text_content().strip() )
        #     return tmp_authors_array
        #
        # return self.parse_publisher(root)
        return ""

    def parse_comments(self, root):
        # description_node = root.xpath('//*[@id="description"]/table//th[contains(text(), "イベント")]/following-sibling::td/a')
        # if description_node:
        #     comments = tostring(description_node[0], method='text',encoding=unicode).strip()
        #     while comments.find('  ') >= 0:
        #         comments = comments.replace('  ',' ')
        #     # Since sanitize strips out line breaks, we will leave this commented out for now...
        #     #comments = sanitize_comments_html(comments)
        #     return comments
        return ""

    def parse_cover(self, root):
        imgcol_node = ''.join(root.xpath('//*[@id="work_left"]//li[@class="slider_item active"]/img/@src'))
        if imgcol_node:
            img_url = 'https:' + imgcol_node.strip()
            return img_url
        return ""

    def parse_gunre(self, root):
        gunre_nodes = root.xpath('//*[@id="work_outline"]//th[contains(text(), "作品形式")]/following-sibling::td//a')
        if gunre_nodes:
            return gunre_nodes[0].text_content().strip()
        return ""

    def parse_monopoly(self, root):
        monopoly_nodes = root.xpath('//div[@id="top_wrapper"]//span[contains(text(), "専売")]')
        if monopoly_nodes:
            return True
        return False

    def parse_publish_date(self, root):
        pub_date_node = root.xpath('//*[@id="work_outline"]//th[contains(text(), "販売日")]/following-sibling::td/a')
        if pub_date_node:
            pub_date_text = pub_date_node[0].text_content().strip()

            if pub_date_text[0] == '2':
                pub_date_text = pub_date_text.replace('年', '/').replace('月', '/').replace('日', '')[:10]
                return pub_date_text
        return ""

    def parse_publisher(self, root):
        publisher_nodes = root.xpath('//*[@id="work_maker"]//*[@class="maker_name"]/a')
        if publisher_nodes:
            return publisher_nodes[0].text_content().strip()
        return ""

    # UNUSE
    def parse_publisher_url(self, root):
        publisher_urls = root.xpath('//*[@id="work_maker"]//*[@class="maker_name"]/a/@href')
        if publisher_urls:
            return publisher_urls[0].strip()
        return ""

    def parse_tags(self, root):
        # Melonbooks has multiple optional sections which can be used as tags depending on the user's preference.
        calibre_tags = list()

        return calibre_tags

    def parse_event(self, root):
        event_node = root.xpath('//*[@id="work_outline"]//th[contains(text(), "イベント")]/following-sibling::td//a')
        if event_node:
            return event_node[0].text_content().strip()
        return ""


class WorkerMelon(WorkerCommon): # Get details

    '''
    Get book details from Melonbooks book page in a separate thread
    '''

    def __init__(self, browser, url, search_item, relevance, result_queue, timeout=40):
        super(WorkerMelon, self).__init__(browser, url, search_item, relevance, result_queue, timeout)

    def createRecord(self):
        record = super(WorkerMelon, self).createRecord(ItemsMelon)
        return record

    def run(self):
        try:
            self.get_details()
        except Exception as e:
            print('get_details failed for url: %r'%self.url)
            print(e)

    def get_details(self):
        try:
            print('Melonbooks book url: %r'%self.url)
            self.browser.set_simple_cookie('AUTH_ADULT','1','www.melonbooks.co.jp')
            raw = self.browser.open_novisit(self.url, timeout=self.timeout).read().strip()
        except Exception as e:
            if e.getcode() == 404:
                print('URL malformed: %r'%self.url)
                return
            attr = getattr(e, 'args', [None])
            attr = attr if attr else [None]
            if isinstance(attr[0], socket.timeout):
                msg = 'Melonbooks timed out. Try again later.'
                print(msg)
            else:
                msg = 'Failed to make details query: %r'%self.url
                print(msg)
            return

        raw = raw.decode('utf-8', errors='replace')

        if '<title>404 - ' in raw:
            print('URL malformed: %r'%self.url)
            return

        try:
            root = fromstring(raw)
        except:
            msg = 'Failed to parse melonbooks details page: %r'%self.url
            print(msg)
            return

        self.parse_details( root, self.search_item )

    def parse_details(self, root, search_item):

        try:
            self.ID = self.parse_id(self.url)
        except:
            print('Error parsing melon id for url: %r'%self.url)
            self.ID = ""

        try:
            self.title = self.parse_title(root)
        except:
            print('Error parsing title for url: %r'%self.url)
            self.title = ""

        try:
            self.authors = self.parse_authors(root)
        except:
            print('Error parsing authors for url: %r'%self.url)
            self.authors = []

        if not self.title or not self.ID:
            print('Could not find title/authors/melon id for %r'%self.url)
            print('Melonbooks: %r Title: %r Authors: %r'%(self.ID, self.title,
                self.authors))
            return

        try:
            self.comments = self.parse_comments(root)
        except:
            print('Error parsing comments for url: %r'%self.url)
            self.comments = ""

        try:
            self.cover_url = self.parse_cover(root)
            # print('INFO cover for: %r'%self.cover_url)
        except:
            print('Error parsing cover for url: %r'%self.url)
            self.cover_url = ""

        self.has_cover = bool(self.cover_url)

        try:
            self.tags = self.parse_tags(root)
        except:
            print('Error parsing tags for url: %r'%self.url)
            self.tags = []

        try:
            self.gunre = self.parse_gunre(root)
        except:
            print('Error parsing gunre for url: %r'%self.url)
            self.gunre = ""

        try:
            self.monopoly = self.parse_monopoly(root)
        except:
            print('Error parsing monopoly for url: %r'%self.url)
            self.monopoly = ""

        try:
            self.pubdate = self.parse_publish_date(root)
            # print('INFO pubdate for: %r'%self.pubdate)
        except:
            print('Error parsing publish date for url: %r'%self.url)
            self.pubdate = ""

        try:
            self.publisher = self.parse_publisher(root)
        except:
            print('Error parsing publisher for url: %r'%self.url)
            self.publisher = ""

        try:
            self.event = self.parse_event(root)
        except:
            print('Error parsing event for url: %r'%self.url)
            self.event = ""

        self.result_queue.append( self )

    def parse_id(self, url):
        return re.search('\/detail\/detail\.php\?product_id=(.*)', url).groups(0)[0]

    def parse_title(self, root):
        title_nodes = root.xpath('//*[@id="description"]/table//th[contains(text(), "タイトル")]/following-sibling::td')
        # print('[DEBUG] Title Parse result : %s'%(len(title_nodes)))
        if title_nodes:
            return title_nodes[0].text_content().strip()
        return ""

    def parse_authors(self, root):
        authors_nodes = root.xpath('//*[@id="description"]/table//th[contains(text(), "作家名")]/following-sibling::td/a')

        if authors_nodes:
            tmp_authors_array = []
            for i, node in enumerate( authors_nodes, 0 ):
                tmp_authors_array.append( node.text_content().strip() )
            return tmp_authors_array

        return self.parse_publisher(root)

    def parse_comments(self, root):
        # description_node = root.xpath('//*[@id="description"]/table//th[contains(text(), "イベント")]/following-sibling::td/a')
        # if description_node:
        #     comments = tostring(description_node[0], method='text',encoding=unicode).strip()
        #     while comments.find('  ') >= 0:
        #         comments = comments.replace('  ',' ')
        #     # Since sanitize strips out line breaks, we will leave this commented out for now...
        #     #comments = sanitize_comments_html(comments)
        #     return comments
        return ""

    def parse_cover(self, root):
        imgcol_node = ''.join(root.xpath('//div[@id="main"]/div[1]//img/@src'))
        if imgcol_node:
            img_url = 'https:' + imgcol_node.strip().split('&width')[0]
            return img_url
        return ""

    def parse_gunre(self, root):
        gunre_nodes = root.xpath('//li[contains(@itemtype ,"Breadcrumb")]//a')
        if gunre_nodes:
            return gunre_nodes[len(gunre_nodes)-1].text_content().strip()
        return ""

    def parse_monopoly(self, root):
        monopoly_nodes = root.xpath('//div[@id="title"]//span[contains(text(), "専売")]')
        if monopoly_nodes:
            return True
        return False

    def parse_publish_date(self, root):
        pub_date_node = root.xpath('//*[@id="description"]/table//th[contains(text(), "発行日")]/following-sibling::td')
        # pub_date_node = root.xpath('//*[@id="work_outline"]/tbody/tr')[0].get("id")
        # print('INFO pubdate for: %r'%pub_date_node)
        if pub_date_node:
            pub_date_text = pub_date_node[0].text_content().strip()

            if pub_date_text[0] == '2':
                return pub_date_text
        return ""

    def parse_publisher(self, root):
        publisher_nodes = root.xpath('//*[@id="description"]/table//th[contains(text(), "サークル名")]/following-sibling::td/a')
        if publisher_nodes:
            return publisher_nodes[0].text_content().strip()
        return ""

    def parse_tags(self, root):
        tag_list = list()
        # tag_nodes = root.xpath('//ul[@class="genreTagList"]//li//a')
        # if tag_nodes:
        #     tag_list = [ tag_node.text_content().strip() for tag_node in tag_nodes ]
        #     return tag_list
        return tag_list

    def parse_event(self, root):
        description_node = root.xpath('//*[@id="description"]/table//th[contains(text(), "イベント")]/following-sibling::td/a')
        if description_node:
            comments = tostring(description_node[0], method='text',encoding=unicode).strip()
            while comments.find('  ') >= 0:
                comments = comments.replace('  ',' ')
            # Since sanitize strips out line breaks, we will leave this commented out for now...
            #comments = sanitize_comments_html(comments)
            return comments
        return ""
