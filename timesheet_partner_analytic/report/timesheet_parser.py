#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (C) 2010-2012 Associazione OpenERP Italia
#   (<http://www.openerp-italia.org>).
#   Copyright(c)2008-2010 SIA 'KN dati'.(http://kndati.lv) All Rights Reserved.
#                   General contacts <info@kndati.lv>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.report import report_sxw
from openerp.report.report_sxw import rml_parse


class Parser(report_sxw.rml_parse):
    accounts = {}
    
    def __init__(self, cr, uid, name, context):        
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            # Analytic report:
            'get_objects': self.get_objects,
            'get_contract_closed': self.get_contract_closed,
            'get_hour_format': self.get_hour_format,
            
            # Timesheet report:
            'get_hours': self.get_hours,            
        })

    def get_domain(self, data):
        ''' Domain composition
        '''
        domain = []
        if data['from_date']:
            domain.append(
                ('date', '>=', '%s 00:00:00' % data['from_date']))
        if data['to_date']:
            domain.append(
                ('date', '<=', '%s 23:59:59' % data['to_date']))
                
        if data.get('account_id', False):
            domain.append(
                ('account_id', '=', data['account_id']))
        return domain        
    
    def get_hours(self, data):
        ''' Get master objects
        '''
        if data is None:
            data = {}

        # Reset report dict:
        self.accounts = {}        
        timesheet_pool = self.pool.get('hr.analytic.timesheet')

        res = {}
        # TODO report work only from wizard
        if data.get('wizard', False): # form wizard:        
            # get list from wizard elements
            domain = []
            from_date = '%s-%s-01' % (
                data['year'], 
                data['month'])
            to_date = '%s-%s-01' % (
                data['year'], 
                '%02d' % (
                    int(data['month']) + 1) if data['month'] != '12' else '01',
                )
            with_task = data.get('with_task', False)    
            
            domain.extend([
                ('date', '>=', from_date), 
                ('date', '<', to_date), 
                ])
                
            timesheet_ids = timesheet_pool.search(
                self.cr, self.uid, domain)
                
            for timesheet in timesheet_pool.browse(
                    self.cr, self.uid, timesheet_ids):
                if timesheet.user_id.name not in res:    
                    res[timesheet.user_id.name] = [
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        ]
                res[timesheet.user_id.name][
                    int(timesheet.date[5:7])] += timesheet.unit_amount
        return res

    def get_contract_closed(self, data):
        ''' Task closed
        '''
        cr = self.cr
        uid = self.uid
        context = {}

        res = {}
        project_pool = self.pool.get('project.project')
        
        domain = self.get_domain(data)
        domain.append(('state', '=', 'close'))
        
        project_ids = project_pool.search(cr, uid, domain, context=context)
        for project in project_pool.browse(cr, uid, project_ids, 
                context=context):
             if project.partner_id not in res:
                 res[project.partner_id] = []                     
             res[project.partner_id].append(project)
        #return sorted(
        #    res.iteritems(), key=lambda x: (x[0].name))
        return res.iteritems()    
        
    def get_objects(self, objects, data):
        ''' Get master objects
        '''
        cr = self.cr
        uid = self.uid
        context = {}
        
        if data is None:
            data = {}

        # Reset report dict:
        timesheet_pool = self.pool.get('hr.analytic.timesheet')
        project_pool = self.pool.get('project.project')
        
        # Load project:
        projects = {}
        project_ids = project_pool.search(cr, uid, [], context=context)
        for project in project_pool.browse(cr, uid, project_ids, 
                context=context):
             projects[project.analytic_account_id] = project

        accounts = {}
        if data.get('wizard', False): # form wizard:
            # get list from wizard elements
            timesheet_ids = timesheet_pool.search(cr, uid, 
                self.get_domain(data), context=context)# order='date')
        else:
            # get list of selected items
            timesheet_ids = [obj.id for obj in objects]
        with_task = data.get('with_task', False)
        
        totals = {}
        for ts in timesheet_pool.browse(
                cr, uid, timesheet_ids, context=context):                
            account = ts.account_id
            if not with_task and account in projects:
                continue # jump task element
            if account not in accounts:
                accounts[account] = []
                totals[account] = 0
                
            accounts[account].append(ts)
            totals[account] += ts.unit_amount
        
        res = []    
        
        previous = 'CHANGE ME'
        for account, ts in sorted(accounts.iteritems(), key=lambda x: (
                x[0].partner_id.name,
                x[0].name,
                )):
            partner = account.partner_id
            if previous == partner.name:
                first = False
            else:
                first = True
                previous = partner.name
            if account in projects:
                project = projects[account]
            else:
                project = False    
            res.append((
                first, # change partner name
                project, # if project browse obj
                partner.name, # partner name
                account.name, # account name
                ts, # intervent
                totals[account], # total hours
                ))
        return res

    def get_hour_format(self, value):
        ''' Format value of float to hours
        '''
        approx = 0.015
        if not value:
            return '0:00'
        
        h = int(value)
        m = int((value - h + approx) * 60)
        return '%s:%02d' % (h, m)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
