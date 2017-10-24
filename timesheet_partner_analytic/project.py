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

class AccountAnalyticAccount(orm.Model):
    """ Model name: AccountAnalyticAccount
    """
    
    _inherit = 'account.analytic.account'

    _columns = {
        'ts_ids': fields.one2many(
            'hr.analytic.timesheet', 'account_id', 
            'Timesheet'),
        }

class HrAnalyticTimesheet(orm.Model):
    """ Model name: HrAnalyticTimesheet
    """
    
    _inherit = 'hr.analytic.timesheet'

    """def onchange_partner_id(self, cr, uid, ids, analytic_partner_id, account_id, 
            context=None): 
        ''' Override onchange account:
        '''    
        res = super(HrAnalyticTimesheet, self).onchange_partner_id(
            cr, uid, ids, analytic_partner_id, account_id, )
        import pdb; pdb.set_trace()    
        return res    

    def on_change_account_id(self, cr, uid, ids, account_id, user_id, 
            context=None): 
        ''' Override onchange account:
        '''    
        res = super(HrAnalyticTimesheet, self).on_change_account_id(
            cr, uid, ids, account_id, user_id)
        import pdb; pdb.set_trace()    
        return res"""
    
class ProjectProject(orm.Model):
    """ Model name: ProjectProject
    """
    
    _inherit = 'project.project'

    # Workflow override:    
    def set_done(self, cr, uid, ids, context=None):
        current_proxy = self.browse(cr, uid, ids, context=context)[0]
        if not current_proxy.date:
            raise osv.except_osv(
                _('Workflow'), 
                _('No end date in project section, insert before close'),
                )
            
        return self.write(cr, uid, ids, {
            'state': 'close'
            }, context=context)

    def _progress_rate_total(self, cr, uid, ids, fields, args, context=None):
        ''' Fields function for calculate 
        ''' 
        res = {}
        for item in self.browse(cr, uid, ids, context=context):
            res[item.id] = {}
            
            # Total manual or total by task:
            if item.planned_manual:
                res[item.id]['all_planned_hours'] = item.planned_manual 
            else:
                res[item.id]['all_planned_hours'] = 0.0
                for task in item.linked_task_ids:
                    res[item.id]['all_planned_hours'] += task.planned_hours
            
            # Total intervent per project:
            res[item.id]['all_effective_hours'] = 0.0 
            for ts in item.ts_ids:
                res[item.id]['all_effective_hours'] += ts.unit_amount

            # Calculate progression:
            if res[item.id]['all_planned_hours']:
                res[item.id]['all_progress_rate'] = 100.0 * \
                    res[item.id]['all_effective_hours'] / \
                        res[item.id]['all_planned_hours']
            else:
                res[item.id]['all_progress_rate'] = 0.0                   
        return res

    _columns = {
        # instead of planned_hours
        'planned_manual': fields.float(
            'Planned H. manual', digits=(16, 3)),
        
        # Total at the date when closed:    
        'planned_total': fields.float(
            'Planned total', digits=(16, 2)),

        # Task:
        'linked_task_ids': fields.one2many(
            'project.task', 'project_id', 
            'Tasks',),
                
        'all_progress_rate': fields.function(
            _progress_rate_total, method=True, 
            type='float', string='Progress rate', store=False,
            multi=True), 
        'all_planned_hours': fields.function(
            _progress_rate_total, method=True, 
            type='float', string='Planned total', store=False,
            multi=True), 
        'all_effective_hours': fields.function(
            _progress_rate_total, method=True, 
            type='float', string='Effective total', store=False,
            multi=True),         
        }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
