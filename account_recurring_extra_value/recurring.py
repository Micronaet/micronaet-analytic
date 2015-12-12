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


class account_analytic_account(orm.Model):
    ''' Change field and override calculation procedure from account obj
    '''
    _inherit = "account.analytic.account"

    # -------------------
    # Override procedure:
    # -------------------
    def _recurring_create_invoice(self, cr, uid, ids, automatic=False, 
            context=None):
        context = context or {}
        invoice_ids = []
        current_date =  time.strftime('%Y-%m-%d')
        if ids:
            contract_ids = ids
        else:
            contract_ids = self.search(cr, uid, [
                ('recurring_next_date','<=', current_date), 
                ('state','=', 'open'), 
                ('recurring_invoices','=', True), 
                ('type', '=', 'contract')])
        if contract_ids:
            cr.execute('''
                SELECT 
                    company_id, array_agg(id) as ids 
                FROM 
                    account_analytic_account 
                WHERE id IN %s GROUP BY company_id
                ''', (tuple(contract_ids), ))
            for company_id, ids in cr.fetchall():
                for contract in self.browse(
                        cr, uid, ids, context = dict(
                            context, 
                            company_id=company_id, 
                            force_company=company_id)):
                    try:
                        invoice_values = self._prepare_invoice(
                            cr, uid, contract, context=context)
                        invoice_ids.append(
                            self.pool['account.invoice'].create(
                                cr, uid, invoice_values, context=context))
                        next_date = datetime.datetime.strptime(
                            contract.recurring_next_date or current_date, 
                            '%Y-%m-%d')
                        interval = contract.recurring_interval
                        if contract.recurring_rule_type == 'daily':
                            new_date = next_date + relativedelta(
                                days=+interval)
                        elif contract.recurring_rule_type == 'weekly':
                            new_date = next_date + relativedelta(
                                weeks=+interval)
                        elif contract.recurring_rule_type == 'monthly':
                            new_date = next_date + relativedelta(
                                months=+interval)
                        else:
                            new_date = next_date + relativedelta(
                                years=+interval)
                        self.write(cr, uid, [contract.id], {
                            'recurring_next_date': 
                                new_date.strftime('%Y-%m-%d')}, context=context)
                        if automatic:
                            cr.commit()
                    except Exception:
                        if automatic:
                            cr.rollback()
                            _logger.exception('Fail to create recurring invoice for contract %s', contract.code)
                        else:
                            raise
        return invoice_ids

    _columns = {
        'recurring_rule_type': fields.selection([
            ('daily', 'Day(s)'),
            ('weekly', 'Week(s)'),
            ('monthly', 'Month(s)'),
            ('bimestra', 'Bimestral(s)'),
            ('trimestral', 'Trimestral(s)'),
            ('quadrimestral', 'Quadrimestral(s)'),
            ('semestral', 'Semestral(s)'),
            ('yearly', 'Year(s)'),
            ], 'Recurrency', 
            help="Invoice automatically repeat at specified interval"),
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
