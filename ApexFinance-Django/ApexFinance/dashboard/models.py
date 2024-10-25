from django.db import models
from decimal import Decimal

# Creates an ETF Holdings to be added to Data Base 
class ETFHolding(models.Model):
    etf_ticker = models.CharField(max_length=10)  # e.g., SPY, VTI, etc.
    stock_symbol = models.CharField(max_length=10)  # e.g., AAPL, MSFT, etc.
    holding_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    etf_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), null=True)
    last_updated = models.DateTimeField(auto_now=True)  # Last updated timestamp for this record

    class Meta:
        unique_together = ('etf_ticker', 'stock_symbol')  # Ensure unique combinations

    def __str__(self):
        return f"{self.etf_ticker} - {self.stock_symbol} ({self.holding_percentage}%)"