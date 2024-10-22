from django.db import models
from django.contrib.auth.models import User # Allows system to associate data with what user
from django.utils import timezone

# Extend the User model with a Profile model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    available_cash = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)  # Store user's balance
    
    def __str__(self):
        return f"{self.user.username} - Balance: ${self.available_cash}"

# Model to store stocks owned by the user
class UserStock(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='stocks') # Link to User (many stocks per user)
    company_name = models.CharField(max_length=255) # Stores the stock token
    stock_quantity = models.PositiveIntegerField(default=0)  # Store how many shares they own
    stock_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the stock at the time of purchase
    stock_purchase_date = models.DateField(default=timezone.now) # Automatically set the date when the stock is purchased

    def __str__(self):
        return f"{self.company_name} owns {self.stock_quantity} shares of {self.company_name}" 
    
    
    
