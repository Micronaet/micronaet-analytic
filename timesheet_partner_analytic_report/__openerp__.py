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
    'name': 'Report wizard for customer to analytic analysis and timesheet',
    'version': '0.0.1',
    'category': 'Report',
    'description': """
        Add customer information for filter analytic account lines 
        """,
    'author': 'Micronaet s.r.l.',
    'website': 'http://www.micronaet.it',
    'depends': [
        'hr',
        'analytic',
        'hr_timesheet',
        'hr_timesheet_invoice',
        'hr_attendance',
        'report',
        'report_aeroo',
        ],
    'init_xml': [],
    'data': [
        'partner_view.xml',
        'report/timesheet_report.xml',
        'report/hours_report.xml',
        'wizard/wizard_analytic_report.view.xml',
        ],
    'demo_xml': [],
    'active': False,
    'installable': True,
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
