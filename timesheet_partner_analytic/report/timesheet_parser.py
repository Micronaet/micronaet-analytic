#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (C) 2010-2012 Associazione OpenERP Italia
#   (<http://www.openerp-italia.org>).
#   Copyright(c)2008-2010 SIA "KN dati".(http://kndati.lv) All Rights Reserved.
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
            'get_lines': self.get_lines,
            
            # Timesheet report:
            'get_hours': self.get_hours,            
        })

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
            from_date = "%s-%s-01" % (
                data['year'], 
                data['month'])
            to_date = "%s-%s-01" % (
                data['year'], 
                '%02d' % (
                    int(data['month']) + 1) if data['month'] != '12' else '01',
                )
            
            domain.extend([
                ('date', '>=', from_date), 
                ('date', '<', to_date), ])
                
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

    def get_objects(self, objects, data):
        ''' Get master objects
        '''
        if data is None:
            data = {}

        # Reset report dict:
        self.accounts = {}        
        timesheet_pool = self.pool.get('hr.analytic.timesheet')

        if data.get('wizard', False): # form wizard:
            # get list from wizard elements
            domain = []
            if data['from_date']:
                domain.append(
                    ('date', '>=', "%s 00:00:00" % data['from_date']))
            if data['to_date']:
                domain.append(
                    ('date', '<=', "%s 00:00:00" % data['to_date']))
            if data.get('account_id', False):
                domain.append(
                    ('account_id', '=', data['account_id']))
            timesheet_ids = timesheet_pool.search(self.cr, self.uid, 
                domain, )# order='date')
        else:
            # get list of selected items
            timesheet_ids = [obj.id for obj in objects]
                

        for timesheet in timesheet_pool.browse(
                self.cr, self.uid, timesheet_ids):
            if timesheet.account_id.name not in self.accounts:
                self.accounts[timesheet.account_id.name] = []
            self.accounts[timesheet.account_id.name].append(timesheet)
        return sorted(self.accounts.keys())

    def get_lines(self, account):
        ''' Get master objects
        '''
        if account not in self.accounts:
            return []
            
        return sorted(self.accounts[account], key=lambda a: a.date)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
