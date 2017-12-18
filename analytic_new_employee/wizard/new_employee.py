# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<http://www.micronaet.it>)
# Developer: Nicola Riolini @thebrush (<https://it.linkedin.com/in/thebrush>)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


import os
import sys
import logging
import openerp
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.tools.translate import _
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)


class HrEmployeeNewWizard(orm.TransientModel):
    ''' Wizard for
    '''
    _name = 'hr.employee.new.wizard'

    # --------------------
    # Wizard button event:
    # --------------------
    def action_done(self, cr, uid, ids, context=None):
        ''' Event for button done
        '''
        if context is None: 
            context = {}        
        
        wiz_browse = self.browse(cr, uid, ids, context=context)[0]
        
        # Pool used:
        user_pool = self.pool.get('res.users')
        product_pool = self.pool.get('product.product')
        employee_pool = self.pool.get('hr.employee')
        
        # ---------------------------------------------------------------------
        # A. Create res.users:
        # ---------------------------------------------------------------------
        user_id = user_pool.create(cr, uid, {
            'name': wiz_browse.name,
            'email': wiz_browse.email,
            'login': wiz_browse.email,
            'password': wiz_browse.password,
            }, context=context)
        
        # ---------------------------------------------------------------------
        # B. Create product.product:
        # ---------------------------------------------------------------------
        product_id = product_pool.create(cr, uid, {
            'name': _('Hour cost of  %s') % wiz_browse.name,
            'type': 'service',
            'standard_price': wiz_browse.cost,
            }, context=context)
        

        # ---------------------------------------------------------------------
        # C. Create hr.employee:
        # ---------------------------------------------------------------------
        employee_id = employee_pool.create(cr, uid, {
            'name': wiz_browse.name,
            'user_id': user_id,
            'product_id': product_id,                    
            }, context=context)
        
        return {
            'type': 'ir.actions.act_window_close'
            }

    _columns = {
        'name': fields.char('First name Last name', size=80, required=True),
        'email': fields.char('Email', size=120, required=True),
        'cost': fields.float('Hour Cost', digits=(16, 2), required=True),
        'password': fields.char('Password', size=64, required=True),
        }
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


