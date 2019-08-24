#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
# from __future__ import (unicode_literals, division, absolute_import,
#                         print_function)

import json, time, os, re, sys, datetime
from urllib import quote, urlencode
from Queue import Queue, Empty
from datetime import datetime
import browser
import worker

from lxml.html import fromstring, tostring

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.exc import SQLAlchemyError

import models

class SiteCommon:

    ID_NAME = ''
    BASE_URL = ''

    def _create_browser_common(self):
        _br = browser.Browser()
        _br.set_handle_equiv(False)
        _br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        return _br

    def create_browser(self):
        _br = self._create_browser_common()
        return _br

    def run_workers(self, workers):
        for w in workers:
            w.start()
            # Don't send all requests at the same time
            time.sleep(0.1)

        while True:
            a_worker_is_alive = False
            for w in workers:
                if w.is_alive():
                    a_worker_is_alive = True
            if not a_worker_is_alive:
                break
        return

    def exec_search(self, title, author=None):
        br = self.create_browser()
        _result_queue = []

        # TODO CUSTOM LINE
        # query = Melonbooks.BASE_URL + '/search/search.php?mode=search&search_disp=&category_id=0&text_type=&text_type=all&'
        # post_data = urlencode({ 'name':title, 'is_end_of_sale':1, 'is_end_of_sale2':1 })

        try:
            # REJECT ADULT FORM
            response = br.open_novisit(query + post_data, timeout=30)
        except Exception as e:
            err = 'Failed to make identify query: %s%s'%(query, post_data)
            print(err)
            print(e)
            return False

        try:
            raw = response.read().strip()
            raw = raw.decode('utf-8', errors='replace')
            if not raw:
                log.error('Failed to get raw result for query: %s%s'%(query, post_data))
                return
            root = fromstring(raw)

        except Exception as e:
            msg = 'Failed to parse melonbooks page for query: %s%s'%(query, post_data)
            print(msg)
            print(e)
            return False

        # TODO CUSTOM LINE
        # all_result = root.xpath('//*[@id="container"]//div[@class="thumb"]/a/@href')
        all_result = null

        matches = []
        for rindex, ritem in enumerate(all_result):
            # TODO CUSTOM LINE
            # matches.append('%s%s'%(Melonbooks.BASE_URL, ritem.strip()))
            matches.append(null)

        if not matches:
            print('No matches found with query: %s%s'%(query, post_data))
            return False

        workers = [worker.Worker(br, url, all_result[i], i, _result_queue) for i, url in
                enumerate(matches)]

        self.run_workers(workers)

        ret_records = []
        for windex, w in enumerate(_result_queue):
            w.printMetadata()
            ret_records.append(w.createRecord())

        return ret_records

    def get_detail_page(self, detail_id):
        _br = self.create_browser()
        _result_queue = []

        # TODO CUSTOM LINE
        # _url = ('%s/detail/detail.php?product_id=%s'%(self.BASE_URL, detail_id))
        _url = "" # TODO CUSTOM LINE

        workers = [worker.Worker(_br, _url, None, 1, _result_queue)]

        self.run_workers(workers)

        ret_records = []
        for windex, w in enumerate(_result_queue):
            w.printMetadata()
            ret_records.append(w.createRecord())

        return ret_records

    def get_ranking(self, week="", type="0", category="1", period="1", rate="-1", mode="category", disp_number="120", pageno="1"):
        br = self.create_browser()

        # TODO CUSTMU LINE
        # query = Melonbooks.BASE_URL + '/ranking/index.php?'
        # post_data = urlencode({
        #     'week':week,
        #     'type':type,                # 販売種別（0:全て、1:販売中、4:予約商品）
        #     'category':category,        # カテゴリ（"":全て、1:同人誌、2～8:各ジャンルなど）
        #     'period':period,            # 集計期間（1:日間、2:週間、3:月間）
        #     'rate':rate,                # 商品種別（-1:全て、0:一般向け、1:成年向け
        #     'mode':mode,                # 検索モード（カテゴリ指定ありの場合、category）
        #     'disp_number':disp_number,  # １ページの取得件数
        #     'pageno':pageno,            # 取得ページ
        # })

        try:
            print(query + post_data)
            # POST REQUESTS
            response = br.open_novisit(query + post_data, timeout=30)

            # RECIEVE RESPONSES
            raw = response.read().strip()
            raw = raw.decode('utf-8', errors='replace')

        except Exception as e:
            err = 'Failed to make identify query: %s%s'%(query, post_data)
            print(err)
            print(e)
            return False

        if not raw:
            log.error('Failed to get raw result for query: %s%s'%(query, post_data))
            return

        root = fromstring(raw)
        # TODO CUSTMU LINE
        # rank_nodes = root.xpath('//div[contains(concat(" ",@class," "),"products")]//div[contains(concat(" ",@class," "),"product")]')

        _timestamp = datetime.now()

        ret_records = []
        for ridx, rnode in enumerate(rank_nodes):
            rank_seq = rank_nodes[ridx].xpath('.//span[contains(concat(" ",@class," "),"rank_")]')[0].text_content().strip()

            print(" THUMB : " + rank_seq)

            record = models.RankingsMelon(
                # 取得日時
                rank_date = _timestamp,
                # ランキング種別
                rank_category = category,
            )
            ret_records.append(record)

        return ret_records

    def prodcutID_from_url(self, url):
        # TODO CUSTOM LINE
        match = []
        # match = re.match(Melonbooks.BASE_URL + "/detail/detail.php\?product_id=(.*)", url)
        if match:
            return match.groups(0)[0]
        return None

    def circleID_from_url(self, url):
        # TODO CUSTOM LINE
        match = []
        # match = re.match(Melonbooks.BASE_URL + "/detail/detail.php\?product_id=(.*)", url)
        if match:
            return match.groups(0)[0]
        return None

    def testrun_search(self, args, session, keyword):
        return True

    def testrun_id(self, args, session, detail_id):
        return True

    def testrun_ranking(self, args, session):
        return True

    def testrun(self, args, session):
        if len(args) < 4:
            self.testrun_search(args, session)
            self.testrun_id(args, session)
            self.testrun_ranking(args, session)
        elif args[2] == "-s" or args[2] == "--search":
            self.testrun_search(args, session, args[3])
        elif args[2] == "-i" or args[2] == "--id":
            self.testrun_id(args, session, args[3])
        elif args[2] == "-r" or args[2] == "--ranking":
            self.testrun_ranking(args, session)
        else:
            print("Bad arguments!! Check -h / --help option!!")
        return True

class Fanza(SiteCommon):

    ID_NAME = 'fanza'
    BASE_URL = 'https://www.dmm.co.jp'

    def create_browser(self):
        _br = self._create_browser_common()
        return _br

    def exec_search(self, title, author=None):
        br = self.create_browser()
        _result_queue = []

        query = Fanza.BASE_URL + '/search/search.php?mode=search&search_disp=&category_id=0&text_type=&text_type=all&'
        post_data = urlencode({ 'name':title, 'is_end_of_sale':1, 'is_end_of_sale2':1 })

        try:
            # REJECT ADULT FORM
            response = br.open_novisit(query + post_data, timeout=30)

        except Exception as e:
            err = 'Failed to make identify query: %s%s'%(query, post_data)
            print(err)
            print(e)
            return False

        try:
            raw = response.read().strip()
            raw = raw.decode('utf-8', errors='replace')
            if not raw:
                log.error('Failed to get raw result for query: %s%s'%(query, post_data))
                return
            root = fromstring(raw)

        except Exception as e:
            msg = 'Failed to parse Fanza page for query: %s%s'%(query, post_data)
            print(msg)
            print(e)
            return False

        # print('[DEBUG] Parse result : %s'%(len(all_result)))
        all_result = root.xpath('//*[@id="container"]//div[@class="thumb"]/a/@href')
        # print('[DEBUG] Parse result : %s'%(len(all_result)))

        matches = []
        for rindex, ritem in enumerate(all_result):
            # print('[DEBUG] Matches Item %s / %s'%(str(rindex),ritem.strip()))
            matches.append('%s%s'%(Fanza.BASE_URL, ritem.strip()))

        if not matches:
            print('No matches found with query: %s%s'%(query, post_data))
            return False

        workers = [worker.WorkerFanza(br, url, all_result[i], i, _result_queue) for i, url in
                enumerate(matches)]

        self.run_workers(workers)

        ret_records = []
        for windex, w in enumerate(_result_queue):
            w.printMetadata()
            ret_records.append(w.createRecord())

        return ret_records

    def get_detail_page(self, detail_id):
        _br = self.create_browser()
        _result_queue = []
        _url = ('%s/dc/doujin/-/detail/=/cid=%s/'%(Fanza.BASE_URL, detail_id))

        workers = [worker.WorkerFanza(_br, _url, None, 1, _result_queue)]

        self.run_workers(workers)

        ret_records = []
        for windex, w in enumerate(_result_queue):
            w.printMetadata()
            ret_records.append(w.createRecord())

        return ret_records

    def get_ranking(self, sort="1", submedia="1", term="1", type="-1"):
        br = self.create_browser()

        _sort_text = "/sort="
        if sort == "1":  # 人気順
            _sort_text = _sort_text + "popular"
        elif sort == "2":  # 販売数順
            _sort_text = _sort_text + "sales"
        else: # デフォルト
            _sort_text = ""

        _submedia_text = "/submedia="
        if submedia == "1":  # 総合
            _submedia_text = _submedia_text + "all"
        elif submedia == "2":  # コミック
            _submedia_text = _submedia_text + "comic"
        elif submedia == "3":  # ＣＧ
            _submedia_text = _submedia_text + "cg"
        elif submedia == "4":  # ゲーム
            _submedia_text = _submedia_text + "game"
        elif submedia == "5":  # ボイス
            _submedia_text = _submedia_text + "voice"
        else: # デフォルト
            _submedia_text = ""

        # 検索期間を決定する
        _term_text_pre = ""
        _term_text_main = "/term="
        if term == "1":
            _term_text_main = _term_text_main + 'per_hour'
        elif term == "2":
            _term_text_main = _term_text_main + 'h24'
        elif term == "3":
            _term_text_main = _term_text_main + 'weekly'
        elif term == "4":
            _term_text_main = _term_text_main + 'monthly'
        elif term == "5":
            _term_text_pre = '/yearly'
            _term_text_main = _term_text_main + 'first/year=' + str( datetime.today().year )
        elif term == "6":
            _term_text_main = _term_text_main + 'total'
        else:
            _term_text_pre = '/yearly'
            _term_text_main = _term_text_main + 'all/year=' + term

        _type_text = "/type="
        if type == "1":  # サークル
            _type_text = _type_text + "maker"
        elif type == "2":  # シリーズ
            _type_text = _type_text + "series"
        else: # デフォルト
            _type_text = ""

        query = Fanza.BASE_URL + '/dc/doujin/-/ranking-all'
        query += _term_text_pre + "/="
        query += _sort_text
        query += _submedia_text
        query += _term_text_main
        query += _type_text

        post_data = ""

        ret_records = []
        for pageno in range(1, 6):
            try:
                print(query + "/page=" + str( pageno ) + "/")
                # POST REQUESTS
                response = br.open_novisit(query + "/page=" + str( pageno ) + "/", timeout=30)

                # RECIEVE RESPONSES
                raw = response.read().strip()
                raw = raw.decode('utf-8', errors='replace')

            except Exception as e:
                err = 'Failed to make identify query: %s%s'%(query, post_data)
                print(err)
                print(e)
                return False

            if not raw:
                log.error('Failed to get raw result for query: %s%s'%(query, post_data))
                return

            root = fromstring(raw)
            rank_nodes = root.xpath('//li[contains(concat(" ",@class," "),"rank-rankListItem")]//div[contains(concat(" ",@class," "),"rank-itemContent")]')

            _timestamp = datetime.now()

            for ridx, rnode in enumerate(rank_nodes):
                rank_seq = rank_nodes[ridx].xpath('.//b[contains(concat(" ",@class," "),"rank-name")]//a/@href')[0].strip().split('i3_ord=')[1]
                rank_seq = str( int(rank_seq) + ( pageno - 1 ) * 20 )

                rank_title = rank_nodes[ridx].xpath('.//b[contains(concat(" ",@class," "),"rank-name")]//a')[0].text_content().strip()

                rank_circle_id = self.circleID_from_url(Fanza.BASE_URL + rank_nodes[ridx].xpath('.//p[@class="rank-circle"]//a/@href')[0].strip())

                rank_circle_name = rank_nodes[ridx].xpath('.//p[@class="rank-circle"]//a')[0].text_content().strip()

                rank_author = ""

                node_tag = rank_nodes[ridx].xpath('.//li[@class="rank-labelListItem"]//a')
                rank_tag = ""
                for _idx, _elem in enumerate(node_tag):
                    if _idx != 0:
                        rank_tag = rank_tag + " & "
                    rank_tag = rank_tag + node_tag[_idx].text_content().strip()

                rank_url = Fanza.BASE_URL + rank_nodes[ridx].xpath('.//b[contains(concat(" ",@class," "),"rank-name")]//a/@href')[0].strip()

                rank_id = self.prodcutID_from_url(rank_url)

                rank_thumb = rank_nodes[ridx].xpath('.//div[@class="rank-imgContent"]//img/@src')[0].strip()

                rank_monopoly = ( len( rank_nodes[ridx].xpath(u'.//li[@class="rank-tagsItem"]/*[text()="FANZA専売"]') ) > 0 )

                rank_tag_gunre = rank_nodes[ridx].xpath('.//li[@class="rank-typeListItem"]/span')[0].text_content().strip()

                rank_price = rank_nodes[ridx].xpath('.//p[contains(concat(" ",@class," "), "c_txt_price")]/strong')[0].text_content().strip().replace(',', '').replace(u'円', '')

                node_point_rate = rank_nodes[ridx].xpath('.//span[@class="c_icon_pointStatus"]')[0].text_content().strip().split('%')[0]
                rank_point = str( int( float( rank_price ) * ( 100.0 / 108.0 ) * ( float( node_point_rate ) / 100.0 ) ) )

                rank_stock = True

                _str_rank_only = " "
                if rank_monopoly:
                    _str_rank_only = "M"

                _str_rank_stock = "x"
                if rank_stock:
                    _str_rank_stock = "o"

                print( _str_rank_only + "[" + rank_seq + "] " + rank_tag_gunre + " / " +  rank_id + " / " + rank_circle_name + " / " + rank_title + " / " + rank_author + " / " + rank_tag)
                # print("   URL : " + rank_url)
                # print(" THUMB : " + rank_thumb)
                # print(" STOCK : " + _str_rank_stock + " ( " + rank_price + " / " + rank_point + " Point )")

                record = models.RankingsFanza(
                    # 取得日時
                    rank_date = _timestamp,
                    # ランキング種別
                    rank_category = submedia,
                    # 集計期間（1:日次、7:週次、30:月次、365:年次、999:総合計）
                    rank_period = term,
                    # 順位
                    rank_seq = rank_seq.split(u"位")[0],
                    # 商品ＩＤ
                    rank_item_id = rank_id,
                    # タイトル名
                    rank_title = rank_title,
                    # サークルＩＤ
                    rank_circle_id = rank_circle_id,
                    # サークル名
                    rank_circle_name = rank_circle_name,
                    # 作者名
                    rank_author = rank_author,
                    # タグ名
                    rank_tag = rank_tag,
                    # 商品ＵＲＬ
                    rank_item_url = rank_url,
                    # サムネイルＵＲＬ
                    rank_thumb = rank_thumb,
                    # 専売フラグ
                    rank_monopoly = rank_monopoly,
                    # ジャンル
                    rank_tag_gunre = rank_tag_gunre,
                    # 価格
                    rank_price = rank_price,
                    # ポイント
                    rank_point = rank_point,
                    # 在庫有無
                    rank_stock = rank_stock,
                )
                ret_records.append(record)

        return ret_records

    def prodcutID_from_url(self, url):
        match = re.match(Fanza.BASE_URL + "/dc/doujin/-/detail/=/cid=(.*)/", url.split('?')[0])
        if match:
            return match.groups(0)[0]
        return None

    def circleID_from_url(self, url):
        match = re.match(Fanza.BASE_URL + "/dc/doujin/-/list/=/article=maker/id=(.*)/", url.split('?')[0])
        if match:
            return match.groups(0)[0]
        return None

    def testrun_search(self, args, session, keyword="Rip@Lip"):
        print(u"◆検索")
        self.exec_search(keyword)
        print("")
        return True

    def testrun_id(self, args, session, detail_id="d_159503"):
        print(u"◆ＩＤ")
        ed_items = self.get_detail_page(detail_id)
        session.add_all(ed_items)
        session.commit()
        print("")
        return True

    def testrun_ranking(self, args, session):
        # ランキング取得
        print(u"◆同人誌（１時間）")
        ed_ranks = self.get_ranking(sort="1", submedia="1", term="1", type="-1")
        session.add_all(ed_ranks)
        session.commit()
        print("")
        print(u"◆コミック（日次）販売数順")
        ed_ranks = self.get_ranking(sort="2", submedia="2", term="2", type="-1")
        session.add_all(ed_ranks)
        session.commit()
        print("")
        print(u"◆ＣＧ（週次）")
        ed_ranks = self.get_ranking(sort="1", submedia="3", term="3", type="-1")
        session.add_all(ed_ranks)
        session.commit()
        print("")
        print(u"◆ゲーム（月次）")
        ed_ranks = self.get_ranking(sort="1", submedia="4", term="4", type="-1")
        session.add_all(ed_ranks)
        session.commit()
        print("")
        print(u"◆ボイス（年次）")
        ed_ranks = self.get_ranking(sort="1", submedia="5", term="5", type="-1")
        session.add_all(ed_ranks)
        session.commit()
        print("")
        print(u"◆同人誌（累計）")
        ed_ranks = self.get_ranking(sort="1", submedia="1", term="6", type="-1")
        session.add_all(ed_ranks)
        session.commit()
        print("")
        print(u"◆同人誌（指定年次）販売数順")
        ed_ranks = self.get_ranking(sort="2", submedia="1", term="2018", type="-1")
        session.add_all(ed_ranks)
        session.commit()
        print("")
        return True

class DLSite(SiteCommon):

    ID_NAME = 'dlsite'
    BASE_URL = 'https://www.dlsite.com'

    def create_browser(self):
        _br = self._create_browser_common()
#        _br.set_simple_cookie('AUTH_ADULT','1','www.melonbooks.co.jp')
        return _br

    def run_workers(self, workers):
        for w in workers:
            w.start()
            # Don't send all requests at the same time
            time.sleep(0.1)

        while True:
            a_worker_is_alive = False
            for w in workers:
                if w.is_alive():
                    a_worker_is_alive = True
            if not a_worker_is_alive:
                break
        return

    def exec_search(self, title, author=None):
        br = self.create_browser()
        _result_queue = []

        query = DLSite.BASE_URL + '/suggest/?'

        post_data = urlencode({'term':title,
                               'site':'adult-jp',
                               'time':int(time.time()),
                               'touch':'0'})

        try:
            # REJECT ADULT FORM
            response = br.open_novisit(query + post_data, timeout=30)
        except Exception as e:
            err = 'Failed to make identify query: %s%s'%(query, post_data)
            print(err)
            print(e)
            return False

        try:
            raw = response.read().strip()
            raw = raw.decode('utf-8', errors='replace')
            if not raw:
                log.error('Failed to get raw result for query: %s%s'%(query, post_data))
                return

        except Exception as e:
            msg = 'Failed to parse melonbooks page for query: %s%s'%(query, post_data)
            print(msg)
            print(e)
            return False

        all_result = json.loads(raw)["work"]

        matches = []
        for rindex, ritem in enumerate(all_result):
            matches.append('%s/maniax/work/=/product_id/%s.html'%(DLSite.BASE_URL, ritem["workno"]))

        if not matches:
            print('No matches found with query: %s%s'%(query, post_data))
            return False

        workers = [worker.WorkerDLSite(br, url, all_result[i], i, _result_queue) for i, url in
                enumerate(matches)]

        self.run_workers(workers)

        ret_records = []
        for windex, w in enumerate(_result_queue):
            w.printMetadata()
            ret_records.append(w.createRecord())

        return ret_records

    def get_detail_page(self, detail_id):
        _br = self.create_browser()
        _result_queue = []

        # TODO CUSTOM LINE
        _url = ('%s/maniax/work/=/product_id/%s.html'%(DLSite.BASE_URL, detail_id))

        workers = [worker.WorkerDLSite(_br, _url, None, 1, _result_queue)]

        self.run_workers(workers)

        ret_records = []
        for windex, w in enumerate(_result_queue):
            w.printMetadata()
            ret_records.append(w.createRecord())

        return ret_records

#    def get_ranking(self, week="", type="0", category="1", period="1", rate="-1", mode="category", disp_number="120", pageno="1"):
    def get_ranking(self, floor="4", period="", category="", sub="", genre="", pageno="1"):
        br = self.create_browser()

        # ショップを決定する
        _floor_text = ""
        if floor == "1":
            _floor_text = "/home"
        elif floor == "2":
            _floor_text = "/comic"
        elif floor == "3":
            _floor_text = "/soft"
        elif floor == "4":
            _floor_text = "/maniax"
        elif floor == "5":
            _floor_text = "/books"
        elif floor == "6":
            _floor_text = "/pro"
        else:
            _floor_text = "/" + floor

        # 検索期間を決定する
        _period_text = ""
        if period == "1":
            _period_text = '/day'
        elif period == "2":
            _period_text = '/week'
        elif period == "3":
            _period_text = '/month'
        elif period == "4":
            _period_text = '/' + str( datetime.today().year )
        elif period == "5":
            _period_text = '/total'
        else:
            _period_text = '/' + period

        query = DLSite.BASE_URL + _floor_text + '/ranking' + _period_text + "?"

        post_map = {}
        if category:
            post_map['category'] = category
        if sub:
            post_map['sub'] = sub
        if genre:
            post_map['genre'] = genre
        if pageno <> "1":
            post_map['pageno'] = pageno
        post_data = urlencode(post_map)

        try:
            print(query + post_data)
            # POST REQUESTS
            response = br.open_novisit(query + post_data, timeout=30)

            # RECIEVE RESPONSES
            raw = response.read().strip()
            raw = raw.decode('utf-8', errors='replace')

        except Exception as e:
            err = 'Failed to make identify query: %s%s'%(query, post_data)
            print(err)
            print(e)
            return False

        if not raw:
            log.error('Failed to get raw result for query: %s%s'%(query, post_data))
            return

        root = fromstring(raw)
        rank_nodes = root.xpath('//table[@id="ranking_table"]/tbody/tr')

        _timestamp = datetime.now()

        ret_records = []
        for ridx, rnode in enumerate(rank_nodes):
            rank_seq = rank_nodes[ridx].xpath('.//div[contains(@class, "rank_no")]')[0].text_content().strip()

            rank_title = rank_nodes[ridx].xpath('.//dt[@class="work_name"]//a')[0].text_content().strip()

            rank_circle_id = self.circleID_from_url(rank_nodes[ridx].xpath('.//dd[@class="maker_name"]//a/@href')[0].strip())

            rank_circle_name = rank_nodes[ridx].xpath('.//dd[@class="maker_name"]//a')[0].text_content().strip()

            rank_author = ""

            # node_tag = rank_nodes[ridx].xpath('.//p[@class="author"]//a[contains(concat(" ",@href," "),"/tags/index.php")]')
            rank_tag = ""
            # for _idx, _elem in enumerate(node_tag):
            #     if _idx != 0:
            #         rank_tag = rank_tag + " & "
            #     rank_tag = rank_tag + node_tag[_idx].text_content().strip()

            rank_url = rank_nodes[ridx].xpath('.//dt[@class="work_name"]//a/@href')[0].strip()

            rank_id = self.prodcutID_from_url(rank_url)

            rank_thumb = rank_nodes[ridx].xpath('.//div[@class="work_thumb"]//img/@src')[0].strip()

            rank_monopoly = ( len( rank_nodes[ridx].xpath(u'.//span[@title="DLsite専売"]') ) > 0 )

            rank_tag_gunre = rank_nodes[ridx].xpath('.//div[contains(@class, "work_category")]')[0].text_content().strip()

            rank_price = rank_nodes[ridx].xpath('.//span[contains(@class, "work_price")]')[0].text_content().strip()

            rank_point = rank_nodes[ridx].xpath('.//span[@class="work_point"]')[0].text_content().strip().split("pt")[0]

            rank_stock = True

            _str_rank_only = " "
            if rank_monopoly:
                _str_rank_only = "M"

            _str_rank_stock = "x"
            if rank_stock:
                _str_rank_stock = "o"

            print( _str_rank_only + "[" + rank_seq + "] " + rank_tag_gunre + " / " +  rank_id + " / " + rank_circle_name + " / " + rank_title)

            record = models.RankingsDLSite(
                # 取得日時
                rank_date = _timestamp,
                # ランキング種別
                rank_category = floor,
                # 集計期間（1:日次、7:週次、30:月次、365:年次、999:総合計）
                rank_period = period,
                # 順位
                rank_seq = rank_seq.split(u"位")[0],
                # 商品ＩＤ
                rank_item_id = rank_id,
                # タイトル名
                rank_title = rank_title,
                # サークルＩＤ
                rank_circle_id = rank_circle_id,
                # サークル名
                rank_circle_name = rank_circle_name,
                # 作者名
                rank_author = rank_author,
                # タグ名
                rank_tag = rank_tag,
                # 商品ＵＲＬ
                rank_item_url = rank_url,
                # サムネイルＵＲＬ
                rank_thumb = rank_thumb,
                # 専売フラグ
                rank_monopoly = rank_monopoly,
                # ジャンル
                rank_tag_gunre = rank_tag_gunre,
                # 価格
                rank_price = rank_price.replace('\\', '').replace(',', '').replace(u"円", ''),
                # ポイント
                rank_point = rank_point,
                # 在庫有無
                rank_stock = rank_stock,
            )
            ret_records.append(record)

        return ret_records

    def prodcutID_from_url(self, url):
        # TODO CUSTOM LINE
        match = re.match(DLSite.BASE_URL + "/maniax/work/=/product_id/(.*)\.html.*", url)
        if match:
            return match.groups(0)[0]
        return None

    def circleID_from_url(self, url):
        # TODO CUSTOM LINE
        match = []
        # match = re.match(Melonbooks.BASE_URL + "/detail/detail.php\?product_id=(.*)", url)
        if match:
            return match.groups(0)[0]
        return None

    def testrun_search(self, args, session, keyword="Stapspats"):
        print(u"◆検索")
        ed_items = self.exec_search(keyword)
        session.add_all(ed_items)
        session.commit()
        print("")
        return True

    def testrun_id(self, args, session, detail_id="RJ257601"):
        print(u"◆ＩＤ")
        ed_items = self.get_detail_page(detail_id)
        session.add_all(ed_items)
        session.commit()
        print("")
        return True

    def testrun_ranking(self, args, session):
        print(u"◆同人誌")
        ed_ranks = self.get_ranking(floor="4", period="1", category="", sub="", genre="", pageno="1")
        session.add_all(ed_ranks)
        session.commit()
        print("")
        return True

class Melonbooks(SiteCommon):

    ID_NAME = 'melon'
    BASE_URL = 'https://www.melonbooks.co.jp'

    def create_browser(self):
        _br = self._create_browser_common()
        _br.set_simple_cookie('AUTH_ADULT','1','www.melonbooks.co.jp')
        return _br

    def exec_search(self, title, author=None):
        br = self.create_browser()
        _result_queue = []

        query = Melonbooks.BASE_URL + '/search/search.php?mode=search&search_disp=&category_id=0&text_type=&text_type=all&'
        post_data = urlencode({ 'name':title, 'is_end_of_sale':1, 'is_end_of_sale2':1 })

        try:
            # REJECT ADULT FORM
            response = br.open_novisit(query + post_data, timeout=30)

        except Exception as e:
            err = 'Failed to make identify query: %s%s'%(query, post_data)
            print(err)
            print(e)
            return False

        try:
            raw = response.read().strip()
            raw = raw.decode('utf-8', errors='replace')
            if not raw:
                log.error('Failed to get raw result for query: %s%s'%(query, post_data))
                return
            root = fromstring(raw)

        except Exception as e:
            msg = 'Failed to parse melonbooks page for query: %s%s'%(query, post_data)
            print(msg)
            print(e)
            return False

        # print('[DEBUG] Parse result : %s'%(len(all_result)))
        all_result = root.xpath('//*[@id="container"]//div[@class="thumb"]/a/@href')
        # print('[DEBUG] Parse result : %s'%(len(all_result)))

        matches = []
        for rindex, ritem in enumerate(all_result):
            # print('[DEBUG] Matches Item %s / %s'%(str(rindex),ritem.strip()))
            matches.append('%s%s'%(Melonbooks.BASE_URL, ritem.strip()))

        if not matches:
            print('No matches found with query: %s%s'%(query, post_data))
            return False

        workers = [worker.WorkerMelon(br, url, all_result[i], i, _result_queue) for i, url in
                enumerate(matches)]

        self.run_workers(workers)

        ret_records = []
        for windex, w in enumerate(_result_queue):
            w.printMetadata()
            ret_records.append(w.createRecord())

        return ret_records

    def get_detail_page(self, detail_id):
        _br = self.create_browser()
        _result_queue = []

        _url = ('%s/detail/detail.php?product_id=%s'%(self.BASE_URL, detail_id))

        workers = [worker.WorkerMelon(_br, _url, None, 1, _result_queue)]

        self.run_workers(workers)

        ret_records = []
        for windex, w in enumerate(_result_queue):
            w.printMetadata()
            ret_records.append(w.createRecord())

        return ret_records

    def get_ranking(self, week="", type="0", category="1", period="1", rate="-1", mode="category", disp_number="120", pageno="1"):
        br = self.create_browser()

        query = Melonbooks.BASE_URL + '/ranking/index.php?'
        post_data = urlencode({
            'week':week,
            'type':type,                # 販売種別（0:全て、1:販売中、4:予約商品）
            'category':category,        # カテゴリ（"":全て、1:同人誌、2～8:各ジャンルなど）
            'period':period,            # 集計期間（1:日間、2:週間、3:月間）
            'rate':rate,                # 商品種別（-1:全て、0:一般向け、1:成年向け
            'mode':mode,                # 検索モード（カテゴリ指定ありの場合、category）
            'disp_number':disp_number,  # １ページの取得件数
            'pageno':pageno,            # 取得ページ
        })

        try:
            print(query + post_data)
            # POST REQUESTS
            response = br.open_novisit(query + post_data, timeout=30)

            # RECIEVE RESPONSES
            raw = response.read().strip()
            raw = raw.decode('utf-8', errors='replace')

        except Exception as e:
            err = 'Failed to make identify query: %s%s'%(query, post_data)
            print(err)
            print(e)
            return False

        if not raw:
            log.error('Failed to get raw result for query: %s%s'%(query, post_data))
            return

        root = fromstring(raw)
        rank_nodes = root.xpath('//div[contains(concat(" ",@class," "),"products")]//div[contains(concat(" ",@class," "),"product")]')

        _timestamp = datetime.now()

        ret_records = []
        for ridx, rnode in enumerate(rank_nodes):
            rank_seq = rank_nodes[ridx].xpath('.//span[contains(concat(" ",@class," "),"rank_")]')[0].text_content().strip()

            rank_title = rank_nodes[ridx].xpath('.//p[@class="title"]//a')[0].text_content().strip()

            rank_circle_id = self.circleID_from_url(Melonbooks.BASE_URL + rank_nodes[ridx].xpath('.//p[@class="circle"]//a/@href')[0].strip())

            rank_circle_name = rank_nodes[ridx].xpath('.//p[@class="circle"]//a')[0].text_content().strip()

            node_author = rank_nodes[ridx].xpath('.//p[@class="author"]//a[contains(concat(" ",@href," "),"search.php")]')
            rank_author = ""
            for _idx, _elem in enumerate(node_author):
                if _idx != 0:
                    rank_author = rank_author + " & "
                rank_author = rank_author + node_author[_idx].text_content().strip()

            node_tag = rank_nodes[ridx].xpath('.//p[@class="author"]//a[contains(concat(" ",@href," "),"/tags/index.php")]')
            rank_tag = ""
            for _idx, _elem in enumerate(node_tag):
                if _idx != 0:
                    rank_tag = rank_tag + " & "
                rank_tag = rank_tag + node_tag[_idx].text_content().strip()

            rank_url = Melonbooks.BASE_URL + rank_nodes[ridx].xpath('.//p[@class="title"]//a/@href')[0].strip()

            rank_id = self.prodcutID_from_url(rank_url)

            rank_thumb = 'https:' + rank_nodes[ridx].xpath('.//div[@class="thumb"]//img/@src')[0].strip().split('&width')[0]

            rank_monopoly = ( len( rank_nodes[ridx].xpath('.//span[@class="monopoly"]') ) > 0 )

            rank_tag_gunre = rank_nodes[ridx].xpath('.//span[@class="tag gunre leader"]/span')[0].text_content().strip()

            rank_price = rank_nodes[ridx].xpath('.//p[@class="price"]/em')[0].text_content().strip().replace(u'\xa5', '\\')

            rank_point = rank_nodes[ridx].xpath('.//p[@class="price"]/span')[0].text_content().strip()

            rank_stock = ( rank_nodes[ridx].xpath('.//p[@class="stock"]')[0].text_content().strip() != u'在庫：-')

            _str_rank_only = " "
            if rank_monopoly:
                _str_rank_only = "M"

            _str_rank_stock = "x"
            if rank_stock:
                _str_rank_stock = "o"

            print( _str_rank_only + "[" + rank_seq + "] " + rank_tag_gunre + " / " +  rank_id + " / " + rank_circle_name + " / " + rank_title + " / " + rank_author + " / " + rank_tag)
            print("   URL : " + rank_url)
            print(" THUMB : " + rank_thumb)
            print(" STOCK : " + _str_rank_stock + " ( " + rank_price + " / " + rank_point + " Point )")

            record = models.RankingsMelon(
                # 取得日時
                rank_date = _timestamp,
                # ランキング種別
                rank_category = category,
                # 集計期間（1:日次、7:週次、30:月次、365:年次、999:総合計）
                rank_period = period,
                # 順位
                rank_seq = rank_seq.split(u"位")[0],
                # 商品ＩＤ
                rank_item_id = rank_id,
                # タイトル名
                rank_title = rank_title,
                # サークルＩＤ
                rank_circle_id = rank_circle_id,
                # サークル名
                rank_circle_name = rank_circle_name,
                # 作者名
                rank_author = rank_author,
                # タグ名
                rank_tag = rank_tag,
                # 商品ＵＲＬ
                rank_item_url = rank_url,
                # サムネイルＵＲＬ
                rank_thumb = rank_thumb,
                # 専売フラグ
                rank_monopoly = rank_monopoly,
                # ジャンル
                rank_tag_gunre = rank_tag_gunre,
                # 価格
                rank_price = rank_price.replace('\\', '').replace(',', ''),
                # ポイント
                rank_point = rank_point,
                # 在庫有無
                rank_stock = rank_stock,
            )
            ret_records.append(record)

        return ret_records

    def prodcutID_from_url(self, url):
        match = re.match(Melonbooks.BASE_URL + "/detail/detail.php\?product_id=(.*)", url)
        if match:
            return match.groups(0)[0]
        return None

    def circleID_from_url(self, url):
        match = re.match(Melonbooks.BASE_URL + "/circle/index.php\?circle_id=(.*)", url)
        if match:
            return match.groups(0)[0]
        return None

    def testrun_search(self, args, session, keyword="柚子奈ひよ"):
        print(u"◆検索")
        self.exec_search(keyword)
        print("")
        return True

    def testrun_id(self, args, session, detail_id="534610"):
        print(u"◆ＩＤ")
        ed_items = self.get_detail_page(detail_id)
        session.add_all(ed_items)
        session.commit()
        print("")
        return True

    def testrun_ranking(self, args, session):
        print(u"◆同人誌")
        ed_ranks = self.get_ranking(week="", type="0", category="1", period="3", rate="0", mode="category", disp_number="100", pageno="1")
        session.add_all(ed_ranks)
        session.commit()
        print(u"◆同人ソフト")
        ed_ranks = self.get_ranking(week="", type="0", category="2", period="3", rate="0", mode="category", disp_number="100", pageno="1")
        session.add_all(ed_ranks)
        session.commit()
        print("")
        print(u"◆同人アイテム")
        ed_ranks = self.get_ranking(week="", type="0", category="3", period="3", rate="0", mode="category", disp_number="20", pageno="1")
        print("")
        print(u"◆コミックス")
        ed_ranks = self.get_ranking(week="", type="0", category="4", period="3", rate="0", mode="category", disp_number="100", pageno="1")
        session.add_all(ed_ranks)
        session.commit()
        print("")
        print(u"◆ゲーム")
        ed_ranks = self.get_ranking(week="", type="0", category="5", period="3", rate="0", mode="category", disp_number="20", pageno="1")
        session.add_all(ed_ranks)
        session.commit()
        print("")
        print(u"◆音楽")
        ed_ranks = self.get_ranking(week="", type="0", category="6", period="3", rate="0", mode="category", disp_number="20", pageno="1")
        session.add_all(ed_ranks)
        session.commit()
        print("")
        print(u"◆映像")
        ed_ranks = self.get_ranking(week="", type="0", category="17", period="3", rate="0", mode="category", disp_number="20", pageno="1")
        session.add_all(ed_ranks)
        session.commit()
        print("")
        print(u"◆グッズ")
        ed_ranks = self.get_ranking(week="", type="0", category="7", period="3", rate="0", mode="category", disp_number="20", pageno="1")
        session.add_all(ed_ranks)
        session.commit()
        print("")
        print(u"◆うりぼうざっか店")
        ed_ranks = self.get_ranking(week="", type="0", category="8", period="3", rate="0", mode="category", disp_number="20", pageno="1")
        session.add_all(ed_ranks)
        session.commit()
        print("")
        return True

if __name__ == '__main__': # tests
    args = sys.argv

    melon = Melonbooks()
    dlsite = DLSite()
    fanza = Fanza()

    # エンジン作成
    from sqlalchemy import create_engine
    url = 'mysql+pymysql://root:root@127.0.0.1:3306/test?charset=utf8'
#    url = 'mysql+pymysql://root:app@127.0.0.1:3333/test?charset=utf8'
    engine = create_engine(url, encoding = "utf-8", echo=True)

    # モデル初期化
    models.create_tables(engine)

    # セッション作成
    Session = sessionmaker(bind=engine)
    session = Session()

    if ( args[1] == "melon" ) :
        melon.testrun(args, session)
    elif ( args[1] == "dlsite" ) :
        dlsite.testrun(args, session)
    elif ( args[1] == "fanza" ) :
        fanza.testrun(args, session)
# elif req_site == 'toranoana':
#     modelItems = models.ItemsToranoana
# elif req_site == 'booth':
#     modelItems = models.ItemsBooth
    else :
        print("No Match Args!!")
