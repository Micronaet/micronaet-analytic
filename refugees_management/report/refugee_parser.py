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
import os
import sys
import logging
import openerp
import openerp.netsvc as netsvc
import openerp.addons.decimal_precision as dp
from openerp.report import report_sxw
from openerp.report.report_sxw import rml_parse
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID#, api
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):        
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_objects': self.get_objects,
        })
    
    def get_objects(self, objects, data=None):    
        ''' Return current record or wizard selection
        '''     
        res = []

        # Readability:
        cr = self.cr
        uid = self.uid
        context = {}        
        if data is None:
            data = {}
        
        # Pool: 
        account_pool = self.pool.get('account.analytic.account')
        partner_pool = self.pool.get('res.partner')
    
        if data.get('from_wizard', False): # no wizard:
            # -----------------------------------------------------------------
            # Wizard 
            # -----------------------------------------------------------------
            return res
        else:    
            # -----------------------------------------------------------------
            # No Wizard:    
            # -----------------------------------------------------------------
            date = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)                
            for apartment in objects:
                refugee_ids = account_pool.get_refugees_per_day(
                    cr, uid, apartment.id, date, return_total=False, 
                    context=context)
                
                res.append((
                    apartment,
                    [partner for partner in partner_pool.browse(
                        cr, uid, refugee_ids, context=context)],
                    date,
                    len(refugee_ids),
                    ))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
