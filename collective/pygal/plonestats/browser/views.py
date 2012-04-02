import logging
from datetime import datetime
from operator import itemgetter
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

import  pygal

logger = logging.getLogger('collective.pygal.plonestats')

class IPloneStatsView(Interface):
    """
    PloneStats view interface
    """


class PloneStatsView(BrowserView):
    """
    PloneStats browser view
    """
    implements(IPloneStatsView)

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()


    def get_keywords(self):
        values = self.portal_catalog.Indexes['Subject'].uniqueValues(withLengths=True)
        values = sorted(values, key=itemgetter(1), reverse=True)
        chart = pygal.Pie()
        chart.title = 'Kewords'
        for value in values:
            chart.add(value[0], value[1])
        return chart.render()

    def get_creator(self):
        values = self.portal_catalog.Indexes['Creator'].uniqueValues(withLengths=True)
        chart = pygal.Bar()
        chart.title = 'Creator'
        for value in values:
            chart.add(value[0], value[1])
        return chart.render()


    def get_types(self):
        values = self.portal_catalog.Indexes['Type'].uniqueValues(withLengths=True)
        chart = pygal.HorizontalBar()
        chart.title = 'Type'
        for value in values:
            chart.add(value[0], value[1])
        return chart.render()


    def get_states(self):
        values = self.portal_catalog.Indexes['review_state'].uniqueValues(withLengths=True)
        chart = pygal.Pie()
        chart.title = 'Review state'
        for value in values:
            chart.add(value[0], value[1])
        return chart.render()


    def _idx_datetime_tuple(self, int_time):
        tt = int_time
        mn = tt % 60
        tt = (tt - mn)/60
        hr = tt % 24
        tt = (tt -hr)/24
        dy = tt % 31
        tt = (tt - dy)/31
        mo = tt % 12
        tt = (tt - mo)/12
        yr = tt
        if mo == 0:
            mo = 12
            yr = yr -1
        t_val = ( ( ( ( yr * 12 + mo ) * 31 + dy ) * 24 + hr ) * 60 + mn )
        assert (t_val == int_time)
        return ( yr, mo, dy, hr, mn )




    def get_created_by_month(self):
        first_created = self.portal_catalog(sort_on='created', sort_limit=1)[0].created
        values = self.portal_catalog.Indexes['created'].uniqueValues(withLengths=True)
        by_month = {}
        min_label = '%i-%02i' % (first_created.year(), first_created.month())
        max_label = '%i-%02i' % ( datetime.now().year,  datetime.now().month)
        for yr in range(first_created.year(), datetime.now().year +1):
            for mo in range(1, 13):
                label =  '%i-%02i' % (yr, mo)
                if min_label <= label <= max_label:
                    by_month[label] = 0
        for value in values:
            dtt = self._idx_datetime_tuple(value[0])
            ymstr = '%i-%02i' % (dtt[0], dtt[1])
            #ymstr = str(dtt[0])
            count = by_month[ymstr]
            by_month[ymstr] = count + value[1]
        tt = by_month.items()
        tt.sort()
        chart = pygal.Line(x_label_rotation=90, legend_font_size=6, fill=True)
        chart.title= 'Added content by month'
        chart.x_labels = [t[0] for t in tt]
        total_items = []
        item_count = 0
        for item in tt:
            item_count += item[1]
            total_items.append(item_count)
        chart.add('Items in DB',total_items)
        chart.add('Additions',[t[1] for t in tt])
        return chart.render()

    def get_created_by_year(self):
        values = self.portal_catalog.Indexes['created'].uniqueValues(withLengths=True)
        by_month = {}
        for value in values:
            dtt = self._idx_datetime_tuple(value[0])
            ymstr = str(dtt[0])
            count = by_month.get(ymstr, 0)
            by_month[ymstr] = count + value[1]
        tt = by_month.items()
        tt.sort()
        chart = pygal.Line()
        chart.title= 'Added content by year'
        chart.x_labels = [t[0] for t in tt]
        chart.add('Additions',[t[1] for t in tt])
        return chart.render()
