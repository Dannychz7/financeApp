from django.contrib import admin
from .models import ETFHolding  # Import your model

# Register the ETFHolding model with the admin site
@admin.register(ETFHolding)
class ETFHoldingAdmin(admin.ModelAdmin):
    list_display = ('etf_ticker', 'stock_symbol', 'holding_percentage', 'etf_price', 'last_updated')
    search_fields = ('etf_ticker', 'stock_symbol')  # Add search capability
    list_filter = ('etf_ticker',)  # Add filter capability by ETF ticker