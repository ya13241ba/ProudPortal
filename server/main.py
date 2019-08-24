
import json, time, os, re, datetime
from urllib import quote, urlencode
from lxml.html import fromstring, tostring

class MELONBOOKS(Source):
    name = ""

    # WEB Get
    def get_book_url(self, identifiers):
        melon_id = identifiers.get(self.ID_NAME, None)
        if melon_id:
            return (self.ID_NAME, melon_id,
                    '%s/detail/detail.php?product_id=%s'%(self.BASE_URL, melon_id))
