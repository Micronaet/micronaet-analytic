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


{
    'name': 'Batch Load modules',
    'version': '0.0.1',
    'category': 'Generic Modules/Batch load',
    'description': """
        (not used, migrated in sync modules)
        Load all modules for this type of installation
        Configuration:
        Accounting: Account analytic
        HR: Assign group presence for all users
        
        """,
    'author': 'Micronaet s.r.l.',
    'website': 'http://www.micronaet.it',
    'depends': [
        'base',
        'hr',
        'report_aeroo',
        'contacts',
        'calendar',
        'analytic',
        #'account_analytic_analysis',
        'hr_attendance',
        'hr_holidays',
        'hr_timesheet',
        #'hr_timesheet_invoice',
        #'hr_timesheet_sheet',
        'partner_addresses',
        #'analytic_contract_hr_expense',
        ],
    'init_xml': [],
    'data': [],
    'demo_xml': [],
    'active': False,
    'installable': True,
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    
