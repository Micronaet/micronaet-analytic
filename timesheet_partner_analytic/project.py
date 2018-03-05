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

selection_state = [
    ('green', 'Green (< 90%)'),
    ('yellow', 'Yellow (>= 90% <100%)'),
    ('red', 'Yellow (>=100%)'),
    ]

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
                
            # Progress state:
            if res[item.id]['all_progress_rate'] < 90.0:
                res[item.id]['progress_state'] = 'green'
            elif res[item.id]['all_progress_rate'] < 100.0:
                res[item.id]['progress_state'] = 'yellow'
            else: # >= 100   
                res[item.id]['progress_state'] = 'red'                
        return res

    # -------------------------------------------------------------------------
    # Store function:
    # -------------------------------------------------------------------------
    def _store_refresh_project_project(self, cr, uid, ids, context=None):
        ''' Change planned_manual in project.project
        '''
        _logger.warning('Update planned_manual in project.project')
        return ids

    def _store_refresh_project_task(self, cr, uid, ids, context=None):
        ''' Change planned_manual in project.task
        '''
        project_ids = []
        for task in self.browse(cr, uid, ids, context=context):
            if task.project_id.id not in project_ids:
                project_ids.append(task.project_id.id)
        _logger.warning(
            'Update project_id, planned_hours in project.task [%s]' % (
                project_ids, ))
        return project_ids

    def _store_refresh_analitic_line(self, cr, uid, ids, context=None):
        ''' Change unit_amount in account.analytic.line hr.analytic.timesheet
        '''
        account_ids = []
        for line in self.browse(cr, uid, ids, context=context):
            if line.account_id.id not in account_ids:
                account_ids.append(line.account_id.id)
                
        project_pool = self.pool.get('project.project')
        project_ids = project_pool.search(cr, uid, [
            ('analytic_account_id', 'in', account_ids),
            ], context=context)
            
        _logger.warning('''
            Update unit_amount, account_id 
            in account.analytic.line or hr.analytic.timesheet
                [account_ids # %s] - [project_ids # %s]
                [%s]
            ''' % (len(account_ids), len(project_ids), project_ids))
        return project_ids

    # Single position of refresh database:        
    _store_refresh = {
        'project.project': (
            _store_refresh_project_project, ['planned_manual'], 10),
        'project.task': (
            _store_refresh_project_task, ['planned_hours', 'project_id'], 10),
        'account.analytic.line': (
            _store_refresh_analitic_line, [
                'account_id', 'unit_amount'], 10),
        'hr.analytic.timesheet': (
            _store_refresh_analitic_line, [
                'account_id', 'unit_amount', 'line_id'], 10),
        # XXX hr.analytic.timesheet?
        }

    _columns = {
        # instead of planned_hours
        'is_practice': fields.boolean('Pratica'),
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
            type='float', string='Progress rate', store=_store_refresh,
            multi=True), 
        'all_planned_hours': fields.function(
            _progress_rate_total, method=True, 
            type='float', string='Planned total', store=_store_refresh,
            multi=True), 
        'all_effective_hours': fields.function(
            _progress_rate_total, method=True, 
            type='float', string='Effective total', store=_store_refresh,
            multi=True),
        'progress_state': fields.function(
            _progress_rate_total, method=True, 
            type='selection', selection=selection_state,
            string='Progress state', store=_store_refresh,
            multi=True),
        }
            
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
