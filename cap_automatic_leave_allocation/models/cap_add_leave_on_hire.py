# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)

class Employee(models.Model):
    _inherit = 'hr.employee'
    
    @api.multi
    def _compute_leaves_count(self):
        all_leaves = self.env['hr.leave.report'].read_group([
            ('employee_id', 'in', self.ids),
            ('holiday_status_id.allocation_type', '!=', 'no'),
            ('holiday_status_id.active', '=', 'True'),
            ('state', '=', 'validate')
        ], fields=['number_of_days', 'employee_id'], groupby=['employee_id'])
        mapping = dict([(leave['employee_id'][0], leave['number_of_days']) for leave in all_leaves])
        for employee in self:
            employee.leaves_count = float_round(mapping.get(employee.id, 0), precision_digits=3)

    @api.model
    def create(self, vals):
        res = super(Employee,self).create(vals)
        _logger.info("Employee Created!")
        _logger.info("PTO Policy Assigned: " + str(res.x_studio_pto_policy_assigned))
        if res.x_studio_pto_policy_assigned == "Yes":
            type = self.env['ir.config_parameter'].get_param('hr.leave.allocation.auto_type')
            leaveType = self.env['hr.leave.type'].search([('name', '=', type)])
            alloc = self.env['hr.leave.allocation'].create({
                'name': 'One Day on DOH',
                'employee_id': res.id,
                'holiday_status_id': leaveType.id,
                'number_of_days': 1,
            })
            alloc.action_approve()
        
        return res