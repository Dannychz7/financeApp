from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Initialize Chrome options (headless mode to avoid opening the browser window)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Optional: Remove this if you want to see the browser

# Automatically manage ChromeDriver with webdriver_manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Prompt user to input ETF symbol
etf_symbol = input("Enter the ETF symbol (e.g., SPY, IVV, VOO, VTI): ").upper()

try:
   # Open Yahoo Finance SPY holdings page
    driver.get(f"https://finance.yahoo.com/quote/{etf_symbol}/holdings")

    # Wait for page to load (simple implicit wait, ideally use WebDriverWait for production)
    driver.implicitly_wait(5)

    # Find the section containing top holdings by XPath or CSS selectors
    # For this example, assume we're scraping data from a table within a certain element
    # Look for the section or table containing top holdings information
    try:
        holdings_section = driver.find_element(By.XPATH, '//*[@data-testid="top-holdings"]')
        percents = holdings_section.find_elements(By.CSS_SELECTOR, 'span.data.yf-1ix710n') # percent is what it should be
        holdings = holdings_section.find_elements(By.CSS_SELECTOR, 'a')

        print(f"Top 10 Holdings for {etf_symbol}:")
        # Iterate through both lists and print each company with its percentage
        for holding, percent in zip(holdings, percents):
            holding_name = holding.text.strip()  # Get the company name
            holding_percent = percent.text.strip()  # Get the percentage
            print(f"{holding_name}: {holding_percent}")

    except Exception as e:
        print("Error locating holdings section:", e)

finally:
    # Close the browser
    driver.quit()