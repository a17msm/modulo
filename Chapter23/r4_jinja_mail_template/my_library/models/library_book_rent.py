# -*- coding: utf-8 -*-
from odoo import models, fields, api


class LibraryBookRent(models.Model):
    _name = 'library.book.rent'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    book_id = fields.Many2one('library.book', 'Book', required=True)
    borrower_id = fields.Many2one('res.partner', 'Borrower', required=True)
    state = fields.Selection([('ongoing', 'Ongoing'), ('returned', 'Returned')],
                             'State', default='ongoing', required=True)
    rent_date = fields.Date(default=fields.Date.today)
    return_date = fields.Date()

    @api.model
    def create(self, vals):
        book_rec = self.env['library.book'].browse(vals['book_id'])  # returns record set from for given id
        book_rec.make_borrowed()
        res = super(LibraryBookRent, self).create(vals)
        res.message_subscribe(partner_ids=[res.borrower_id.id])
        if res.return_date:
            res.activity_schedule('mail.mail_activity_data_call', date_deadline=res.return_date)
        return res

    def book_return(self):
        self.ensure_one()
        self.book_id.make_available()
        self.write({
            'state': 'returned',
            'return_date': fields.Date.today()
        })

    def book_return_reminder(self):
        template_id = self.env.ref('my_library.book_return_reminder')
        self.message_post_with_template(template_id.id)