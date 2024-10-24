from django import template
import datetime

register = template.Library()

@register.filter
def get_price(stock_data, company_name):
    return stock_data.get(company_name)