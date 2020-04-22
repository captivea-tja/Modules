# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning

_logger = logging.getLogger(__name__)

class HolidaysAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    @api.multi
    def _automate_leave(self, autoApprove):
        type = self.env['ir.config_parameter'].get_param('hr.leave.allocation.auto_type')
        leaveType = self.env['hr.leave.type'].search([('name', '=', type)])
        if self.is_leap_year(date.today().year):
            _logger.info("This year is a leap year!")
            for record in self.env['hr.employee'].search([]):
                if record.x_studio_field_pE3V6 and record.x_studio_pto_policy_assigned == "Yes":
                    dateToday = date.today()
                    today = str(dateToday.month) + "_" + str(dateToday.day)
                    doh = str(record.x_studio_field_pE3V6.month) + "_" + str(record.x_studio_field_pE3V6.day)
                    _logger.info("DOH: " + doh)
                    _logger.info("Today: " + today)
                    _logger.info("Current Leaves Left: " + str(record.leaves_count))
                    if doh == today:
                        yearsEmp = dateToday.year - record.x_studio_field_pE3V6.year
                        allocationTag = record.name + "_" + str(dateToday)
                        _logger.info("Allocation Awarded!!")
                        _logger.info(allocationTag)
                        _logger.info(self.search([('name', '=', allocationTag)]))
                        _logger.info("%s years of employment!" % yearsEmp)
                        if not self.search([('name', '=', allocationTag)]):
                            if 0 < yearsEmp and yearsEmp < 5:
                                alloc = self.create({
                                    'name': allocationTag,
                                    'employee_id': record.id,
                                    'holiday_status_id': leaveType.id,
                                    'number_of_days': self.days_to_allocate(record.leaves_count, 5, 7.5),
                                })
                            elif  5 <= yearsEmp and yearsEmp < 10:
                                alloc = self.create({
                                    'name': allocationTag,
                                    'employee_id': record.id,
                                    'holiday_status_id': leaveType.id,
                                    'number_of_days': self.days_to_allocate(record.leaves_count, 10, 15),
                                })
                            elif 10 <= yearsEmp:
                                alloc = self.create({
                                    'name': allocationTag,
                                    'employee_id': record.id,
                                    'holiday_status_id': leaveType.id,
                                    'number_of_days': self.days_to_allocate(record.leaves_count, 15, 22.5),
                                })
                            if autoApprove:
                                alloc.action_approve()
                        else:
                            _logger.info("Record Already Exists!")
        else:
            _logger.info("This year is not a leap year!")
            for record in self.env['hr.employee'].search([]):
                if record.x_studio_field_pE3V6 and record.x_studio_pto_policy_assigned == "Yes":
                    dateToday = date.today()
                    today = str(dateToday.month) + "_" + str(dateToday.day)
                    doh = str(record.x_studio_field_pE3V6.month) + "_" + str(record.x_studio_field_pE3V6.day)
                    _logger.info("DOH: " + doh)
                    _logger.info("Today: " + today)
                    _logger.info("Current Leaves Left: " + str(record.leaves_count))
                    if doh == "2_29":
                        doh = "3_1"
                    if doh == today:
                        yearsEmp = dateToday.year - record.x_studio_field_pE3V6.year
                        allocationTag = record.name + "_" + str(dateToday)
                        _logger.info("Allocation Awarded!!")
                        _logger.info(allocationTag)
                        _logger.info("%s years of employment!" % yearsEmp)
                        _logger.info(self.search([('name', '=', allocationTag)]))
                        if not self.search([('name', '=', allocationTag)]):
                            if 0 < yearsEmp and yearsEmp < 5:
                                _logger.info("40 Hours to Award")
                                alloc = self.create({
                                    'name': allocationTag,
                                    'employee_id': record.id,
                                    'holiday_status_id': leaveType.id,
                                    'number_of_days': self.days_to_allocate(record.leaves_count, 5, 7.5),
                                })
                            elif  5 <= yearsEmp and yearsEmp < 10:
                                _logger.info("80 Hours to Award")
                                alloc = self.create({
                                    'name': allocationTag,
                                    'employee_id': record.id,
                                    'holiday_status_id': leaveType.id,
                                    'number_of_days': self.days_to_allocate(record.leaves_count, 10, 15),
                                })
                            elif 10 <= yearsEmp:
                                _logger.info("120 Hours to Award")
                                alloc = self.create({
                                    'name': allocationTag,
                                    'employee_id': record.id,
                                    'holiday_status_id': leaveType.id,
                                    'number_of_days': self.days_to_allocate(record.leaves_count, 15, 22.5),
                                })
                            if autoApprove:
                                alloc.action_approve()
                        else:
                            _logger.info("Record Already Exists!")
            
    def is_leap_year(self, year):
        if ((year % 400 == 0) or ((year % 4 == 0) and (year % 100 != 0))):
            return True
        else:
            return False

    def days_to_allocate(self, current, allocation, max):
        if current + allocation > max:
            return max - current if max - current > 0 else 0
        else:
            return allocation