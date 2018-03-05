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
            'get_contract_closed': self.get_practice_closed, # XXX used?
            'get_hour_format': self.get_hour_format,
            'get_list_partner_task_closed': self.get_list_partner_task_closed,
            
            # Timesheet report:
            'get_hours': self.get_hours,            
        })

    def get_list_partner_task_closed(self, partner_id):
        ''' get partner project list for partner passed
        '''
        return self.practice_closed.get(partner_id, [])
        
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

    def get_practice_closed(self, data):
        ''' Task closed only practice!
        '''
        cr = self.cr
        uid = self.uid
        context = {}

        res = {}
        project_pool = self.pool.get('project.project')
        
        domain = self.get_domain(data)
        domain.extend([
            ('state', '=', 'close'),
            ('is_practice', '=', True),
            ])
        
        project_ids = project_pool.search(cr, uid, domain, context=context)
        for project in project_pool.browse(cr, uid, project_ids, 
                context=context):
             if project.partner_id.id not in res:
                 res[project.partner_id.id] = []                     
             res[project.partner_id.id].append(project)
        return res
        
    def get_objects(self, objects, data):
        ''' Get master objects
        '''
        cr = self.cr
        uid = self.uid
        context = {}
        
        # ---------------------------------------------------------------------
        # Get list of current project closed by partner:
        # ---------------------------------------------------------------------
        self.practice_closed = self.get_practice_closed(data)
        
        if data is None:
            data = {}

        # Reset report dict:
        timesheet_pool = self.pool.get('hr.analytic.timesheet')
        project_pool = self.pool.get('project.project')
        
        # Load project (link analytic account - project):
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
        with_project = data.get('with_project', False)

        # ---------------------------------------------------------------------        
        # Create accounts database (list of timesheet)
        # ---------------------------------------------------------------------        
        totals = {}
        current_partner_ids = []
        for ts in timesheet_pool.browse(
                cr, uid, timesheet_ids, context=context):                
            account = ts.account_id # Timesheet element
            
            # Test practice: 
            if not with_task and account in projects and \
                    projects[account].is_practice:
                continue # jump practice (no contract)
                
            # Test practice: 
            if not with_project and account in projects and \
                    not projects[account].is_practice:
                continue # jump project (no practice)
            
            # (always pricelist)    
            partner = account.partner_id # readability
            if partner.id not in current_partner_ids:
                current_partner_ids.append(partner.id)

            if account not in accounts:
                accounts[account] = []
                totals[account] = 0
                
            accounts[account].append(ts)
            totals[account] += ts.unit_amount

        # ---------------------------------------------------------------------        
        # Partner task completed test:
        # ---------------------------------------------------------------------        
        for partner_id, projects in self.practice_closed.iteritems():
            if partner_id not in current_partner_ids:                
                # Create empty record for generate a partner in list
                accounts[projects[0].analytic_account_id] = []
                #totals[account] = 0
        
        res = []
        previous = 'CHANGE ME'
        for account, ts in sorted(accounts.iteritems(), key=lambda x: (
                x[0].partner_id.name, x[0].name)):
            partner = account.partner_id
            mode == 'pricelist'
            
            if previous == partner.name:
                first = False
            else:
                first = True
                previous = partner.name
            if account in projects:
                project = projects[account]
                if projects[account].is_practice:
                    mode == 'practice'
                else:
                    mode == 'contract'
            else:
                project = False    
            res.append((
                mode,
                first, # change partner name
                project, # if project browse obj
                partner, # partner
                account.name, # account name
                ts, # intervent
                totals.get(account, 0),# total hours TODO check when no partner
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
