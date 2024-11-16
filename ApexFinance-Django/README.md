Current Bugs that need fixing:
[x] Keep all stock tickers in CAPS
[] Update ETF or MUTALFUNDS with current price, not closing price
[] Update ETF, so when you buy it buys current price
[] Add "End of day total portifo sum"
[] Fix UI for Sign up and Sign in Pages
[] Fix logout screen for settings page

How to access admin panel that shows "everything" in the database:
    - run the server
    - navigate to http://127.0.0.1:8000/admin/
    - sign in with the admin username and password 
        - this username and password work for any login page as well


Date: Saturday, October 19th, 2024
User: Daniel Chavez

Things added:
    - Added a sign-up option for new users
    - Added a new Model to the database called Profile, and User Stocks
    - Added a way to associate stock data and cash amount to a certain User
    - Added a register page inside "Users" app
    - Added admin access to view, add, or delete user data in the data base
        - Admin has access to view cash amount, and stocks owned by a user
    - Added signals.py to "Users" app to allow the front end and backend to 
      communicate with each other and assocate which data belonoged to which user
    - Added forms.py to "Users" app to redirect users to the create a new account
    - Threw in some debugging code (Currently commented out) around the views.py to ensure stock data was working
    - Added a sign-out option in "settings" app
    - Added a better view of user infor in "settings" app (User can see email, usernmane, and option to change password)