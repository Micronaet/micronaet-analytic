# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2001-2014 Micronaet SRL (<http://www.micronaet.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
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


class HrAnalyticTimesheet(orm.Model):
    ''' Add onchange event
    '''
    _inherit = 'hr.analytic.timesheet'

    # ----------
    # on change:
    # ----------
    def onchange_partner_id(self, cr, uid, ids, partner_id, account_id, 
            context=None):
        ''' Reset account when change partner
        '''
        res = {}
        if not account_id or not partner_id:
            return res
        
        acc_partner_id = self.pool('account.analytic.account').browse(
            cr, uid, account_id, context=context).partner_id.id
         
        # Account without partner or equal to selected > nothing    
        if not acc_partner_id or partner_id == acc_partner_id:
            return res
        
        # Partner different:    
        res['value'] = {}
        res['value']['account_id'] = False # Reset account        
        return res
            
    _columns = {
        # Override related partner:
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        }

        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
