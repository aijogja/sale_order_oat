# -*- coding: utf-8 -*-

from openerp import models, fields, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    oat = fields.Float(string='OAT (%)')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    oat = fields.Float(string='OAT (%)')

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        ret_val = super(SaleOrderLine, self)._prepare_order_line_invoice_line(cr, uid, line, account_id=False, context=None)
        if not line.invoiced:
            ret_val['oat'] = line.oat
        return ret_val

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False, context=None):
        ret_val = super(SaleOrderLine, self).product_id_change(
            cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag, context=context)
        if partner_id:
            contract_obj = self.pool.get('account.analytic.account')
            contract_ids = contract_obj.search(cr, uid,
                [
                    ['type', '=', 'contract'],
                    ['state', '=', 'open'],
                    ['partner_id', '=', partner_id]
                ],
                context=context
            )
            contract = contract_obj.browse(cr, uid, contract_ids)
        ret_val['value']['oat'] = contract.oat
        return ret_val


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_dpp = fields.Float(
        string='Total DPP',
        compute='_compute_total_dpp',
        store=True
    )
    total_oat = fields.Float(
        string='Total OAT',
        compute='_compute_total_oat',
        store=True,
    )

    @api.depends('amount_untaxed')
    def _compute_total_dpp(self):
        for record in self:
            record.total_dpp = record.amount_untaxed + record.total_oat

    @api.depends('amount_untaxed')
    def _compute_total_oat(self):
        for record in self:
            total_oat = 0
            for line in record.order_line:
                oat = (float(line.oat * line.price_subtotal)/100)
                total_oat += oat
            record.total_oat = total_oat

    @api.multi
    def _amount_all(self, field_name, arg):
        ret_val = super(SaleOrder, self)._amount_all(field_name, arg)
        for order in self:
            total_tax = 0
            total_oat = 0
            for line in order.order_line:
                oat = (float(line.oat * line.price_subtotal)/100)
                tax = (line.price_subtotal + oat) * line.tax_id.amount
                total_tax += tax
                total_oat += oat
            amount_total = order.amount_untaxed + total_tax + total_oat
            ret_val[order.id]['amount_tax'] = total_tax
            ret_val[order.id]['amount_total'] = amount_total
        return ret_val


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    oat = fields.Float(string='OAT (%)')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    total_dpp = fields.Float(
        string='Total DPP',
        compute='_compute_total_dpp',
        store=True
    )
    total_oat = fields.Float(
        string='Total OAT',
        compute='_compute_total_oat',
        store=True,
    )

    @api.one
    @api.depends('amount_untaxed')
    def _compute_total_dpp(self):
        self.total_dpp = self.amount_untaxed + self.total_oat

    @api.one
    @api.depends('amount_untaxed')
    def _compute_total_oat(self):
        total_oat = 0
        for line in self.invoice_line:
            oat = (float(line.oat * line.price_subtotal)/100)
            total_oat += oat
        self.total_oat = total_oat

    @api.one
    @api.depends('invoice_line.price_subtotal', 'invoice_line.oat', 'tax_line.amount')
    def _compute_amount(self):
        # hitung total oat dan amount tax
        total_oat = 0
        total_tax = 0
        for line in self.invoice_line:
            oat = (float(line.oat * line.price_subtotal)/100)
            tax = (line.price_subtotal + oat) * line.invoice_line_tax_id.amount
            total_oat += oat
            total_tax += tax
        # save data
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
        self.amount_tax = total_tax
        self.amount_total = self.amount_untaxed + self.amount_tax + total_oat
