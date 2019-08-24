#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

import json

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.exc import SQLAlchemyError

import falcon

import models

def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

class DetailResource:
    def __init__(self, _session):
        self.session = _session

    def __get_model_items(self, req_site):
        modelItems = null
        if not req_site:
            return modelItems
        elif req_site == 'melon':
            modelItems = models.ItemsMelon
        elif req_site == 'dlsite':
            modelItems = models.ItemsDLSite
        elif req_site == 'fanza':
            modelItems = models.ItemsFanza
        # elif req_site == 'toranoana':
        #     modelItems = models.ItemsToranoana
        # elif req_site == 'booth':
        #     modelItems = models.ItemsBooth
        return modelItems

    def on_post(self, req, resp):
        # postパラメーターを取得
        body = req.stream.read()
        data = json.loads(body)

        modelItems = self.__get_model_items(req_site)


        # パラメーターの取得
        name = data['name']

        msg = {
            "message": "Hello, " + name
        }
        res.body = json.dumps(msg)

        # ext = mimetypes.guess_extension(req.content_type)
        # name = '{uuid}{ext}'.format(uuid=uuid.uuid4(), ext=ext)
        # image_path = os.path.join(self._storage_path, name)
        #
        # with io.open(image_path, 'wb') as image_file:
        #     while True:
        #         chunk = req.stream.read(self._CHUNK_SIZE_BYTES)
        #         if not chunk:
        #             break
        #
        #         image_file.write(chunk)
        #
        # resp.status = falcon.HTTP_201
        # resp.location = '/images/' + name

    def on_get(self, req, resp):
        req_site = req.get_param('site')
        req_id = req.get_param('id')

        # required params
        modelItems = self.__get_model_items(req_site)
        if not modelItems:
            resp.status = falcon.HTTP_400
            return

        record = session.query(modelItems).filter(modelItems.item_id==req_id).one_or_none()

        if not record :
            resp.status = falcon.HTTP_404
            return

        response_body = {
            'site': req_site,
            'item_id': record.item_id,
            'title': record.title,
            'authors': record.authors,
            'comments': record.comments,
            'cover_url': record.cover_url,
            'has_cover': record.has_cover,
            'tags': record.tags,
            'gunre': record.gunre,
            'monopoly': record.monopoly,
            'pubdate': date_handler(record.pubdate),
            'publisher': record.publisher,
            'event': record.event,
        }

        resp.media = response_body
        return

class RankingResource:
    def __init__(self, _session):
        self.session = _session

    def on_get(self, req, resp):
        req_site = req.get_param('site')

        # required params
        if not req_site:
            resp.status = falcon.HTTP_400
            return

        if req_site == 'melon':
            modelRannkings = models.RankingsMelon
        elif req_site == 'dlsite':
            modelRannkings = models.RankingsDLSite
        elif req_site == 'fanza':
            modelRannkings = models.RankingsFanza
        # elif req_site == 'toranoana':
        #     modelRannkings = models.RankingsToranoana
        # elif req_site == 'booth':
        #     modelRannkings = models.RankingsBooth
        else:
            resp.status = falcon.HTTP_400
            return

        recordset = session.query(modelRannkings).filter(
        modelRannkings.item_id==req_id).All()

        if not recordset :
            resp.status = falcon.HTTP_404
            return

        response_rankings = []
        response_body = { 'site': req_site, 'rankings': response_rankings }
        for ridx, record in enumerate(recordset):
            response_rankings.append({
                'id': record.id,
                'rank_date': date_handler(record.rank_date),
                'rank_category': record.rank_category,
                'rank_period': record.rank_period,
                'rank_seq': record.rank_seq,
                'rank_item_id': record.rank_item_id,
                'rank_title': record.rank_title,
                'rank_circle_id': record.rank_circle_id,
                'rank_circle_name': record.rank_circle_name,
                'rank_author': record.rank_author,
                'rank_tag': record.rank_tag,
                'rank_item_url': record.rank_item_url,
                'rank_thumb': record.rank_thumb,
                'rank_monopoly': record.rank_monopoly,
                'rank_tag_gunre': record.rank_tag_gunre,
                'rank_price': record.rank_price,
                'rank_point': record.rank_point,
                'rank_stock': record.rank_stock,
            })

        resp.media = response_body
        return

class StaticResource:
    def __init__(self, _dirname):
        self.dirname = _dirname

    def on_get(self, req, resp, filename):
        # do some sanity check on the filename
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/html'
        respath = "front\\" + self.dirname + "\\" + filename
        print(respath)
        with open(respath, 'r') as f:
            resp.body = f.read()

if __name__ == '__main__':

    # エンジン作成
    print("> Create DB Connection...")
    from sqlalchemy import create_engine
    url = 'mysql+pymysql://root:root@localhost/test?charset=utf8'
    engine = create_engine(url, encoding = "utf-8", echo=True)

    # セッション作成
    Session = sessionmaker(bind=engine)
    session = Session()

    print("> Setting API...")
    app = falcon.API()
    app.add_route('/api/detail', DetailResource(session))
    app.add_route('/static/main/{filename}', StaticResource("main"))
    app.add_route('/static/uikit/css/{filename}', StaticResource("uikit\\css"))
    app.add_route('/static/uikit/js/{filename}', StaticResource("uikit\\js"))

    from wsgiref import simple_server
    httpd = simple_server.make_server("127.0.0.1", 6543, app)
    try:
        print("> START SERVER...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    print("> SHUTDOWN SERVER...")
    httpd.server_close()
