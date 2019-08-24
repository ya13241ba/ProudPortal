# -*- coding: utf-8 -*-
import sys
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RankingsCommon:
    # [001] ID
    id = Column('id', Integer, primary_key = True)
    # [002] 取得日時
    rank_date = Column('rank_date', DateTime, index=True)
    # [003] ランキング種別
    rank_category = Column('rank_category', Integer, index=True)
    # [003] 集計期間（1:日次、7:週次、30:月次、365:年次、999:総合計）
    rank_period = Column('rank_period', Integer, index=True)
    # [002] 順位
    rank_seq = Column('rank_seq', Integer, index=True)
    # [002] 商品ＩＤ
    rank_item_id = Column('rank_item_id', String(20))
    # [002] タイトル名
    rank_title = Column('rank_title', String(200))
    # [002] サークルＩＤ
    rank_circle_id = Column('rank_circle_id', String(20))
    # [002] サークル名
    rank_circle_name = Column('rank_circle_name', String(100))
    # [002] 作者名
    rank_author = Column('rank_author', String(100))
    # [002] タグ名
    rank_tag = Column('rank_tag', String(200))
    # [002] 商品ＵＲＬ
    rank_item_url = Column('rank_item_url', String(200))
    # [002] サムネイルＵＲＬ
    rank_thumb = Column('rank_thumb', String(200))
    # [002] 専売フラグ
    rank_monopoly = Column('rank_monopoly', Boolean)
    # [002] ジャンル
    rank_tag_gunre = Column('rank_tag_gunre', String(200))
    # [002] 価格
    rank_price = Column('rank_price', String(10))
    # [002] ポイント
    rank_point = Column('rank_point', String(10))
    # [002] 在庫有無
    rank_stock = Column('rank_stock', Boolean)

class ItemsCommon:
    item_id = Column('item_id', String(20), primary_key = True)
    title = Column('title', String(200))
    authors = Column('authors', String(100))
    comments = Column('comments', String(200))
    cover_url = Column('cover_url', String(100))
    has_cover = Column('has_cover', Boolean)
    tags = Column('tags', String(200))
    gunre = Column('gunre', String(200))
    monopoly = Column('monopoly', Boolean)
    pubdate = Column('pubdate', Date)
    publisher = Column('publisher', String(100))
    event = Column('event', String(100))

class ItemTagsCommon:
    item_id = Column('item_id', String(20), primary_key = True)
    tag_id = Column('tag_id', String(15), primary_key = True)
    tag_name = Column('tag_name', String(100))
    tag_url = Column('tag_url', String(100))

# class TagsMaster:
#     tag_id = Column('tag_id', String(15), primary_key = True)
#     tag_name = Column('tag_name', String(100))
#     tag_url = Column('tag_url', String(100))

class RankingsMelon(Base, RankingsCommon):
    __tablename__ = 'rankings_melon'

class RankingsDLSite(Base, RankingsCommon):
    __tablename__ = 'rankings_dlsite'

class RankingsFanza(Base, RankingsCommon):
    __tablename__ = 'rankings_fanza'

class ItemsMelon(Base, ItemsCommon):
    __tablename__ = 'items_melon'

class ItemsDLSite(Base, ItemsCommon):
    __tablename__ = 'items_dlsite'

class ItemsFanza(Base, ItemsCommon):
    __tablename__ = 'items_fanza'

class ItemTagsFanza(Base, ItemTagsCommon):
    __tablename__ = 'itemtags_fanza'

def create_tables(_engine):
    Base.metadata.create_all(_engine)
