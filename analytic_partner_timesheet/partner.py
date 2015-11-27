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

class AccountAnalyticLine(orm.Model):
    ''' Add extra field to analytic line
    '''
    _inherit = 'account.analytic.line'
    
    # --------------------------------------
    # Override function that create invoice:
    # --------------------------------------
    def invoice_cost_create(self, cr, uid, ids, data=None, context=None):
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoices = []
        if context is None:
            context = {}
        if data is None:
            data = {}

        # use key (partner/account, company, currency)
        # creates one invoice per key
        invoice_grouping = {}

        currency_id = False
        # prepare for iteration on journal and accounts
        for line in self.browse(cr, uid, ids, context=context):

       
            # -----------------------------------------------------------------
            # NOTE: OVERRIDE:
            # TODO: Conf / Sale: Usa i listini per gestire i prezzi ai clienti             
            if line.account_id.pricelist_id:
                pricelist_id = line.account_id.pricelist_id
                currency = pricelist_id.currency_id.id
            else:
                pricelist_id = \
                    line.analytic_partner_id.property_product_pricelist
                currency = pricelist_id.currency_id.id
            # -----------------------------------------------------------------

            key = (
                line.account_id.id,
                line.account_id.company_id.id,
                currency,
                )
            invoice_grouping.setdefault(key, []).append(line)

        for (key_id, company_id, currency_id
                ), analytic_lines in invoice_grouping.items():
            # key_id is an account.analytic.account
            
            # -----------------------------------------------------------------
            # NOTE: OVERRIDE:
            partner = analytic_lines[0].analytic_partner_id or analytic_lines[
                0].account_id.partner_id  # will be the same for every line
            # -----------------------------------------------------------------

            curr_invoice = self._prepare_cost_invoice(
                cr, uid, partner, company_id, currency_id, analytic_lines, 
                context=context)
            invoice_context = dict(
                context, lang=partner.lang,
                # set force_company in context so the correct product 
                # properties are selected (eg. income account)
                force_company=company_id,  
                # set company_id in context, so the correct default journal 
                # will be selected
                company_id=company_id)  
            last_invoice = invoice_obj.create(
                cr, uid, curr_invoice, context=invoice_context)
            invoices.append(last_invoice)

            # use key (product, uom, user, invoiceable, analytic account, 
            # journal type)
            # creates one invoice line per key
            invoice_lines_grouping = {}
            for analytic_line in analytic_lines:
                account = analytic_line.account_id
                if (not partner) or not (pricelist_id): # 2 type of pl
                    raise osv.except_osv(
                        _('Error!'), 
                        _('Contract incomplete. Please fill in the Customer '
                            'and Pricelist fields for %s.') % (account.name))

                if not analytic_line.to_invoice:
                    raise osv.except_osv(
                        _('Error!'), 
                        _('Trying to invoice non invoiceable line for %s.') % (
                            analytic_line.product_id.name))

                key = (analytic_line.product_id.id,
                    analytic_line.product_uom_id.id,
                    analytic_line.user_id.id,
                    analytic_line.to_invoice.id,
                    analytic_line.account_id,
                    analytic_line.journal_id.type)
                invoice_lines_grouping.setdefault(key, []).append(
                    analytic_line)

            # finally creates the invoice line
            for (product_id, uom, user_id, factor_id, account, journal_type
                    ), lines_to_invoice in invoice_lines_grouping.items():
                curr_invoice_line = self._prepare_cost_invoice_line(
                    cr, uid, last_invoice,
                    product_id, uom, user_id, factor_id, account, 
                    lines_to_invoice,
                    journal_type, data, 
                    context=context)

                invoice_line_obj.create(cr, uid, curr_invoice_line, 
                    context=context)
            self.write(cr, uid, [l.id for l in analytic_lines], {
                'invoice_id': last_invoice}, context=context)
            invoice_obj.button_reset_taxes(cr, uid, [last_invoice], context)
        return invoices
    
    _columns = {
        'analytic_partner_id': fields.many2one('res.partner', 'Partner'),
        }

# Override report:
class analytic_entries_report(osv.osv):
    _name = "analytic.entries.report"
    _description = "Analytic Entries Statistics"
    _auto = False
    
    _columns = {
        'date': fields.date('Date', readonly=True),
        'user_id': fields.many2one('res.users', 'User',readonly=True),
        'name': fields.char('Description', size=64, readonly=True),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'currency_id': fields.many2one('res.currency', 'Currency', 
            required=True),
        'account_id': fields.many2one('account.analytic.account', 'Account', 
            required=False),
        'general_account_id': fields.many2one('account.account', 
            'General Account', required=True),
        'journal_id': fields.many2one('account.analytic.journal', 'Journal', 
            required=True),
        'move_id': fields.many2one('account.move.line', 'Move', 
            required=True),
        'product_id': fields.many2one('product.product', 'Product', 
            required=True),
        'product_uom_id': fields.many2one('product.uom', 
            'Product Unit of Measure', required=True),
        'amount': fields.float('Amount', readonly=True),
        'unit_amount': fields.integer('Unit Amount', readonly=True),
        # TDE FIXME master: rename into nbr_entries
        'nbr': fields.integer('# Entries', readonly=True),  
    }
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'analytic_entries_report')
        cr.execute("""
            create or replace view analytic_entries_report as (
                 select
                     min(a.id) as id,
                     count(distinct a.id) as nbr,
                     a.date as date,
                     a.user_id as user_id,
                     a.name as name,
                     a.analytic_partner_id as partner_id,
                     a.company_id as company_id,
                     a.currency_id as currency_id,
                     a.account_id as account_id,
                     a.general_account_id as general_account_id,
                     a.journal_id as journal_id,
                     a.move_id as move_id,
                     a.product_id as product_id,
                     a.product_uom_id as product_uom_id,
                     sum(a.amount) as amount,
                     sum(a.unit_amount) as unit_amount
                 from
                     account_analytic_line a, account_analytic_account analytic
                 where analytic.id = a.account_id
                 group by
                     a.date, a.user_id,a.name,a.analytic_partner_id,
                     a.company_id,a.currency_id,
                     a.account_id,a.general_account_id,a.journal_id,
                     a.move_id,a.product_id,a.product_uom_id
            )
        """
        )

class HrAnalyticTimesheet(orm.Model):
    ''' Add onchange event
    '''
    _inherit = 'hr.analytic.timesheet'

    # ----------
    # on change:
    # ----------
    def onchange_partner_id(
            self, cr, uid, ids, analytic_partner_id, account_id, context=None):
        ''' Reset account when change partner
        '''
        res = {}
        if not account_id or not analytic_partner_id:
            return res
        
        acc_partner_id = self.pool('account.analytic.account').browse(
            cr, uid, account_id, context=context).partner_id.id
         
        # Account without partner or equal to selected > nothing    
        if not acc_partner_id or analytic_partner_id == acc_partner_id:
            return res
        
        # Partner different:    
        res['value'] = {}
        res['value']['account_id'] = False # Reset account        
        return res
           
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
