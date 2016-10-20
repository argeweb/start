from __future__ import unicode_literals
import decimal

from argeweb.libs.wtforms import fields

TextField = object

from .db import *
from .ndb import *


class GeoPtPropertyField(TextField):

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                lat, lon = valuelist[0].split(',')
                self.data = '%s,%s' % (
                    decimal.Decimal(lat.strip()),
                    decimal.Decimal(lon.strip()),)

            except (decimal.InvalidOperation, ValueError):
                raise ValueError('Not a valid coordinate location')
