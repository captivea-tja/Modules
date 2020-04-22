# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}
            
        res = super(SaleOrderLine,self).product_id_change()
        
        _logger.info(self.tax_id)
        _logger.info(self.order_partner_id.name)
        exempts = self.env['x_exemptions'].search([('x_studio_contact', '=', self.order_partner_id.id)])
        if exempts:
            for rec in exempts:
                _logger.info(rec.x_name)
                _logger.info('All States?')
                if rec.x_studio_all_states:
                    _logger.info('Yes, all states exempt.')
                    _logger.info('Validated?')
                    if rec.x_studio_validated:
                        _logger.info('Yes, Validated.')
                        _logger.info('Expired?')
                        if rec.x_studio_expiration_date > date.today():
                            _logger.info('Not Expired.')
                            self.tax_id = self.env['account.tax'].search([('name', '=', 'Exempt')])
                        else:
                            _logger.info('Expired.')
                            res['warning'] = {'title': _('Exemption Expired'), 'message': _('This customer has an AllStates Exemption but the Document has expired.')}
                    else:
                        res['warning'] = {'title': _('Exemption Not Validated'), 'message': _('This customer has an AllStates Tax Exemption but the Document has not been validated.')}
                if rec.x_studio_multistate:
                    _logger.info('Yes, to Multistate. Match To:')
                    _logger.info(self.order_id.partner_shipping_id.state_id.name)
                    if self.order_id.partner_shipping_id.state_id in rec.x_studio_multistate:
                        _logger.info('Validated?')
                        if rec.x_studio_validated:
                            _logger.info('Yes, Validated.')
                            _logger.info('Expired?')
                            if rec.x_studio_expiration_date > date.today():
                                _logger.info('Not Expired.')
                                self.tax_id = self.env['account.tax'].search([('name', '=', 'Exempt')])
                            else:
                                res['warning'] = {'title': _('Exemption Expired'), 'message': _('This customer has a Tax Exemption for this state but the Document has expired.')}
                        else:
                            res['warning'] = {'title': _('Exemption Not Validated'), 'message': _('This customer has a Tax Exemption for this state but the Document has not been validated.')}
                                
                                
                    #_logger.info('Validated?')
                    #if rec.x_studio_validated:
                        #_logger.info('Yes, Validated.')
                        #_logger.info('Expired?')
                        #if rec.x_studio_expiration_date > date.today():
                            #_logger.info('Not Expired.')
                            #_logger.info('Is state in list?')
                            #if self.order_partner_id.state_id in rec.x_studio_multistate:
                                #_logger.info('Yes')
                                #self.tax_id = self.env['account.tax'].search([('name', '=', 'Exempt')])
                        #else:
                            #_logger.info('Expired.')
                            #res['warning'] = {'title': _('Exemption Expired'), 'message': _('The Expiration Date for the Multistate Exemption Document has passed.')}
        return res