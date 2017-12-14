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
    
    def get_refugees_per_day(
            self, cr, uid, apartment_id, date, return_total=True, 
            context=None):
        ''' Search total presence for apartment this date
        '''
        presence_pool = self.pool.get('refugee.apartment.presence')
        
        domain = [
            # Apartent:
            ('apartment_id', '=', apartment_id),
            
            # Range of date:
            ('from_date', '<=', date),
            '|',
            ('to_date', '>=', date),
            ('to_date', '=', False),            
            ]
        
        presence_ids = presence_pool.search(cr, uid, domain, context=context)
        if return_total:
            return len(presence_ids)
        
        # else return refugee list:
        return [item.refugee_id.id for item in presence_pool.browse(
            cr, uid, presence_ids, context=context)]
        
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
        #'apartment_total': fields.float('Max refugee'),
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
    
    def load_presence_attendee(self, cr, uid, ids, context=None):
        ''' Load current refugee in apartment 
        '''        
        account_pool = self.pool.get('account.analytic.account')
        attendant_pool = self.pool.get('refugee.lesson.attendant')
        
        lesson_proxy = self.browse(cr, uid, ids, context=context)[0]

        # Delete previous attendant:
        attendant_ids = [item.id for item in lesson_proxy.attendant_ids]
        attendant_pool.unlink(cr, uid, attendant_ids, context=context)
        
        # Get list of attendant:        
        refugee_ids = account_pool.get_refugees_per_day(cr, uid, 
            lesson_proxy.course_apartment_id.id, 
            lesson_proxy.date, 
            return_total=False, 
            context=context)
        
        # Create attandant:
        for refugee_id in refugee_ids: 
            attendant_pool.create(cr, uid, {
                'refugee_id': refugee_id,
                'lesson_id': ids[0],
                }, context=context)
        return True
        
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

    def _get_total_refugee_today(self, cr, uid, ids, fields, args, context=None):
        ''' Fields function for calculate 
        '''
        res = {}
        today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        for item_id in ids:
            res[item_id] = self.get_refugees_per_day(
                cr, uid, item_id, today, 
                return_total=True, context=context,
                )
        return res        

    @api.multi
    def _get_image(self, name, args):
        return dict((p.id, tools.image_get_resized_images(p.image)) for p in self)

    @api.one
    def _set_image(self, name, value, args):
        return self.write({'image': tools.image_resize_image_big(value)})

    @api.multi
    def _has_image(self, name, args):
        return dict((p.id, bool(p.image)) for p in self)
    
    _columns = {
        'total_refugee_today': fields.function(
            _get_total_refugee_today, method=True, 
            type='integer', string='Tot. ref.', store=False), 
                        
        'image': fields.binary('Image', filters=None),
        'image_small': fields.function(
            _get_image, 
            fnct_inv=_set_image,
            string='Small-sized image', type='binary', multi='_get_image',
            store={
                'account.analytic.account': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help='Resize image'),
        'image_medium': fields.function(
            _get_image, 
            fnct_inv=_set_image,
            string='Small-sized image', type='binary', multi='_get_image',
            store={
                'account.analytic.account': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help='Resize image'),
            
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

        'from_date': fields.date('From date', required=True),
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
