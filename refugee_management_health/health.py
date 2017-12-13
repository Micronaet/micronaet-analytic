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

class ResPartnerHealth(orm.Model):
    """ Model name: Res Partner Health
    """    
    _name = 'res.partner.health'
    _description = 'Refugee health'
    _order = 'date'
    
    def open_detail(self, cr, uid, ids, context=None):
        """ Button event
        """    
        return {
            'type': 'ir.actions.act_window',
            'name': _('Health detail'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_id': ids[0],
            'res_model': 'res.partner.health',
            #'view_id': view_id, # False
            'views': [(False, 'form'),(False, 'tree')],
            'domain': [],
            'context': context,
            'target': 'current', # 'new'
            'nodestroy': False,
            }
     
    _columns = {
        'date': fields.date('Date', required=True),
        'name': fields.char('Subject', size=80, required=True),
        'doctor': fields.char('Doctor', size=80), 
        'diagnose': fields.text('Diagnose'),
        'recipe': fields.text('Recipe'),
        'note': fields.text('Note'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        }
                
    _defaults = {
        'date': lambda *x: datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
        }

class ResPartner(orm.Model):
    """ Model name: ResPartner
    """    
    _inherit = 'res.partner'
    
    _columns = {
        'health_ids': fields.one2many(
            'res.partner.health', 'partner_id', 'Health status'),
        }    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
