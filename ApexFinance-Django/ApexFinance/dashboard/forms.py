from django import forms
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


class TradeStockForm(forms.Form):
    TRADE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]
    ORDER_TYPE_CHOICES = [
        ('shares', 'Shares'),
        ('cash', 'Cash Amount'),
    ]

    trade_type = forms.ChoiceField(choices=TRADE_CHOICES, label='Trade Type', widget=forms.RadioSelect)
    order_type = forms.ChoiceField(choices=ORDER_TYPE_CHOICES, label='Order in', widget=forms.RadioSelect)
    stock_quantity = forms.DecimalField(min_value=0.01, label='Quantity/Amount', max_digits=10, decimal_places=2)