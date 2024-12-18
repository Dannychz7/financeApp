from django.contrib import admin
from .models import Profile, UserStock, StockTransaction  # Import your models

# Create an inline admin descriptor for UserStock model
class UserStockInline(admin.TabularInline):  # TabularInline for a table-like view
    model = UserStock  # Specify which model to include
    extra = 0  # Number of extra blank fields to display

# Register the Profile model with UserStock as inline
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'available_cash')  # Columns to display in the admin list view
    inlines = [UserStockInline]  # Include the inline view for UserStock

admin.site.register(Profile, ProfileAdmin)  # Register Profile with custom admin options

# Register the UserStock model without inlines
class UserStockAdmin(admin.ModelAdmin):
    list_display = ('profile', 'company_name', 'stock_quantity', 'stock_price', 'stock_purchase_date')  # Display fields

admin.site.register(UserStock, UserStockAdmin)  # Register UserStock model

class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('profile', 'company_name', 'stock_quantity', 'stock_price', 'transaction_type', 'transaction_date')
    list_filter = ('profile', 'transaction_type')
    search_fields = ('company_name',)

admin.site.register(StockTransaction, StockTransactionAdmin)