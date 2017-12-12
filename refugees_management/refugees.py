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

class AccountAnalyticAccount(orm.Model):
    """ Model name: AccountAnalyticAccount (for Apartment and Lesson)
    """    
    _inherit = 'account.analytic.account'
    
    _columns = {
        # ---------------------------------------------------------------------
        # Apartment:
        # ---------------------------------------------------------------------
        'is_apartment': fields.boolean('Apartment'),
        'apartment_id': fields.many2one(
            'res.partner', 'Apartment', 
            domain=[('is_apartment', '=', True)]),
            
        # Related partner fields:
        'street': fields.related(
            'apartment_id', 'street',
            type='char', string='Street', readonly=True),
        'city': fields.related(
            'apartment_id', 'city',
            type='char', string='City', readonly=True),
        # TODO extra fields from res.partner    
        
        # ---------------------------------------------------------------------
        # Course:
        # ---------------------------------------------------------------------
        'is_course': fields.boolean('Course'),

        # Period:
        'from_date': fields.date('From date'),
        'to_date': fields.date('To date'),

        # Default element:
        'course_apartment_id': fields.many2one(
            'account.analytic.account', 'Default Apartment', 
            domain=[('is_apartment', '=', True)]),
        'teacher_id': fields.many2one(
            'res.users', 'Default Teacher', 
            #domain=[('is_teacher', '=', True)],
            ),
        'course_total': fields.float('Total hour', digits=(16, 3)),
        }
        
# -----------------------------------------------------------------------------
# Course:
# -----------------------------------------------------------------------------
class HrAnalyticTimesheet(orm.Model):
    """ Model name: Hr Analytic Timesheet
    """    
    _inherit = 'hr.analytic.timesheet'
    
    _columns = {
        # For lesson timesheet:
        'course_apartment_id': fields.many2one(
            'account.analytic.account', 'Apartment', 
            domain=[('is_apartment', '=', True)]),        
        }

class AccountAnalyticAccount(orm.Model):
    """ Model name: AccountAnalyticAccount (for Apartment and Lesson)
    """    
    _inherit = 'account.analytic.account'
    
    _columns = {
        'lesson_ids': fields.one2many(
            'hr.analytic.timesheet', 'account_id', 'Lesson'),
        }

class RefugeeLessonAttendant(orm.Model):
    """ Model name: Refugees Course Attendant
    """    
    _name = 'refugee.lesson.attendant'
    _description = 'Lesson attendant'
    _order = 'refugee_id'
    _rec_name = 'lesson_id'
    
    _columns = {
        'lesson_id': fields.many2one('hr.analytic.timesheet', 'Lesson'),
        'refugee_id': fields.many2one('res.partner', 'Refugee',
            domain=[('is_refugee', '=', True)],
            ),

        # Related:
        'date': fields.related(
            'lesson_id', 'date', 
            type='date', string='Date', store=True),    
        'course_id': fields.related(
            'lesson_id', 'account_id', 
            type='many2one', relation='account.analytic.account', 
            string='Course', store=True),
        'teacher_id': fields.related(
            'lesson_id', 'user_id', 
            type='many2one', relation='res.users', 
            string='Teacher', store=True),            
        }

class RefugeeApartmentAttendant(orm.Model):
    """ Model name: Refugees Apartment presence
    """    
    _name = 'refugee.apartment.presence'
    _description = 'Apartment precence'
    _order = 'from_date'
    _rec_name = 'refugee_id'
    
    _columns = {
        'apartment_id': fields.many2one(
            'account.analytic.account', 'Apartment'),
        'refugee_id': fields.many2one('res.partner', 'Refugee',
            domain=[('is_refugee', '=', True)],
            ),

        'from_date': fields.date('From date'),
        'to_date': fields.date('To date'),            
        }

class HrAnalyticTimesheet(orm.Model):
    """ Model name: Hr Analytic Timesheet
    """    
    _inherit = 'hr.analytic.timesheet'
    
    _columns = {
        'attendant_ids': fields.one2many(
            'refugee.lesson.attendant', 'lesson_id', 
            'Attendant'),
        }

# -----------------------------------------------------------------------------
# Apartment
# -----------------------------------------------------------------------------
class RefugeeApartmentPrecence(orm.Model):
    """ Model name: Refugees Apartment Presence
    """    
    _name = 'refugee.apartment.presence'
    _description = 'Apertment presence'
    _order = 'refugee_id'
    _rec_name = 'refugee_id'
    
    _columns = {
        'apartment_id': fields.many2one(
            'account.analytic.account', 'Apartment',
            domain=[('is_apartment', '=', True)], 
            ),
        'refugee_id': fields.many2one('res.partner', 'Refugee',
            domain=[('is_refugee', '=', True)],
            ),

        # Period:
        'from_date': fields.date('From date'),
        'to_date': fields.date('To date'),            
        }
    
# -----------------------------------------------------------------------------
# COMMON
# -----------------------------------------------------------------------------
class ResPartner(orm.Model):
    """ Model name: Partner (for refugee and teacher extra data)
    """    
    _inherit = 'res.partner'
    
    _columns = {
        'is_refugee': fields.boolean('Refugee'),
        'is_apartment': fields.boolean('Apartment'),
        'presence_ids': fields.one2many(
            'refugee.apartment.presence', 'refugee_id', 
            'Presence'),
        }

class ResPartner(orm.Model):
    """ Model name: Partner (for refugee and teacher extra data)
    """    
    _inherit = 'res.users'
    
    _columns = {
        'is_teacher': fields.boolean('Is teacher'),
        }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
