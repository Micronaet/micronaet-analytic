# -*- coding: utf-8 -*-
###############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<http://www.micronaet.it>)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import os
import sys
import logging
import openerp
import openerp.netsvc as netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)
'''class AccountAnalyticLine(orm.Model):
    """ Add extra information for manage partner in analytic line
    """
    
    _inherit = 'account.analytic.line'

    _columns = {
        'ts_partner_id': fields.many2one('res.partner', 'Partner'),
        }

class HrAnalyticTimesheet(orm.Model):
    """ Add extra information for manage partner in analytic line
        Override function are inserted for keep reporting 
        TODO test reporting bug (only first element work)
    """
    
    _inherit = 'hr.analytic.timesheet'

    # Override functions:
    def create(self, cr, uid, vals, context=None):
        """
        Create a new record for a model
        @param cr: cursor to database
        @param uid: id of current user
        @param vals: provides a data for new record
        @param context: context arguments, like lang, time zone
        
        @return: returns a id of new record
        """            
        if 'ts_partner_id' in vals:
            vals['partner_id'] = vals['ts_partner_id']
        res_id = super(HrAnalyticTimesheet, self).create(
            cr, uid, vals, context=context)            
        return res_id
        
    def write(self, cr, uid, ids, vals, context=None):
        """
        Update redord(s) comes in {ids}, with new value comes as {vals}
        return True on success, False otherwise
    
        @param cr: cursor to database
        @param uid: id of current user
        @param ids: list of record ids to be update
        @param vals: dict of new values to be set
        @param context: context arguments, like lang, time zone
        
        @return: True on success, False otherwise
        """
        if 'ts_partner_id' in vals:
            vals['partner_id'] = vals['ts_partner_id']    
        res = super(HrAnalyticTimesheet, self).write(
            cr, uid, ids, vals, context=context)
        return res
    '''

class AnalyticEntriesReport(orm.Model):
    ''' Set float for hours
    '''
    _inherit = "analytic.entries.report"
    
    _columns = {
        'unit_amount': fields.float('Unit Amount', readonly=True),
        }
    
class CalendarEvent(orm.Model):

    _inherit = "calendar.event"
    
    _columns = {
        'partner_id':fields.many2one('res.partner', 'Partner'),
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
