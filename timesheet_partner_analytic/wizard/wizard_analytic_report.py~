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

# WIZARD PRINT REPORT ########################################################
class mrp_production_status_wizard(osv.osv_memory):
    ''' Parameter for product status per day
    '''    
    
    _name = 'account.analytic.report.wizard'
    _description = 'Report analytic line'
    
    # Button events:
    def print_report(self, cr, uid, ids, context=None):
        ''' Redirect to report passing parameters
        ''' 
        wiz_proxy = self.browse(cr, uid, ids)[0]

        datas = {}
        if wiz_proxy.report_type == 'analytic':
            report_name = 'partner_timesheet_report'
        else:
            report_name = 'hours_analytic_timesheet_report'
            
        datas['wizard'] = True # started from wizard
        datas['from_date'] = wiz_proxy.from_date or False
        datas['to_date'] = wiz_proxy.to_date or False
        datas['account_id'] = wiz_proxy.account_id.id or False
        #datas['partner_id'] = wiz_proxy.partner_id.id or False

        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': datas,
        }
        
    _columns = {
        'report_type': fields.selection([
            ('analytic', 'Analytic report'),
            ('timesheet', 'Timesheet report'),
            ], 'Report type', required=True),
        'account_id': fields.many2one('account.analytic.account', 'Account'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        
        'from_date': fields.date('From', help='Date >='),
        'to_date': fields.date('To', help='Date <'),
        
        'month': fields.selection([
            ('01', 'January'),
            ('02', 'February'),
            ('03', 'March'),
            ('04', 'April'),
            ('05', 'May'),
            ('06', 'June'),
            ('07', 'July'),
            ('08', 'Agoust'),
            ('09', 'September'),
            ('10', 'October'),
            ('11', 'November'),
            ('12', 'December'),
            ], 'Month'),
        'year': fields.integer('Year'),        
        }
        
    _defaults = {
        'report_type': lambda *x: 'analytic',
        'to_date': datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
        'month': datetime.now().strftime("%m"), 
        'year': datetime.now().strftime("%Y"),
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
