# from odoo import models, fields, api


# class estate(models.Model):
#     _name = 'estate.estate'
#     _description = 'estate.estate'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100



from odoo import fields, models 
from dateutil.relativedelta import relativedelta


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "First model in Real Estate Addon"

    name = fields.Char('Property Name', required=True)
    description = fields.Text('Property Description')
    postcode = fields.Char("Postcode")
    date_availability = fields.Date("Availability Date", copy=False, default= lambda self: fields.Date.today() + relativedelta(months=3))
    expected_price = fields.Float("Expected price", required=True)
    selling_price = fields.Float("Selling price", readonly=True, copy=False)
    bedrooms = fields.Integer("Number of bedrooms", default=2)
    living_area = fields.Integer("Living Area")
    facades = fields.Integer("Facades")
    garage = fields.Boolean("Garage")
    garden = fields.Boolean('Garden')
    garden_area = fields.Integer("Garden Area")
    garden_orientation = fields.Selection(
        string="Garden orientation",
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')]
    )
    active = fields.Boolean("Active", default=True)
    state = fields.Selection(string="State", selection=[('new', 'New'), ('offerAccepted', 'Offer Accepted'),('offerReceived', 'offerReceived'), ('sold', 'Sold'), ('cancelled', 'Cancelled')], required=True, default='new', copy=False)





