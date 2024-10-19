from django.contrib import admin
from .models import Profile, UserStock  # Import your models

# Register the Profile model
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'available_cash')  # Columns to display in the admin list view

admin.site.register(Profile, ProfileAdmin)  # Register Profile with custom admin options

# Register the UserStock model
class UserStockAdmin(admin.ModelAdmin):
    list_display = ('profile', 'company_name', 'stock_quantity', 'stock_price')  # Display fields

admin.site.register(UserStock, UserStockAdmin)  # Register UserStock model