from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Initialize Chrome options (headless mode to avoid opening the browser window)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Optional: Remove this if you want to see the browser

# # Automatically manage ChromeDriver with webdriver_manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
   # Open Yahoo Finance SPY holdings page
    driver.get("https://finance.yahoo.com/quote/SPY/holdings")

    # Wait for page to load (simple implicit wait, ideally use WebDriverWait for production)
    driver.implicitly_wait(5)

    # Find the section containing top holdings by XPath or CSS selectors
    # For this example, assume we're scraping data from a table within a certain element
    # Look for the section or table containing top holdings information
    try:
        holdings_section = driver.find_element(By.XPATH, '//*[@data-testid="top-holdings"]')
        percents = holdings_section.find_elements(By.CSS_SELECTOR, 'span.data.yf-1ix710n') # percent is what it should be
        holdings = holdings_section.find_elements(By.CSS_SELECTOR, 'a')
#       print(holdings)

        print("Top 10 Holdings for SPY:")
        for holding in holdings[:10]:  # Limit to top 10
            company_name = holding.text
            percent = percents.text
            print(company_name, " and ", percent)

    except Exception as e:
        print("Error locating holdings section:", e)

finally:
    # Close the browser
    driver.quit()