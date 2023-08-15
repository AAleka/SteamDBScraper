#!/usr/bin/env python3

import os.path
import pickle
import random

import time
import json
import shutil

from selenium_stealth import stealth
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service

import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


def send_email(n, sender, password, receiver_email, receiver_name, save_name):
    html = '''
        <html>
            <body style="justify-content:center; padding-bottom: 20px; background-color: LightPink;">
                <div style="text-align: center;">
                    <h1>Hello %s!<h1>
                    <h2>Your daily deals from Steam Dealer 666 await!</h2>
                    <p>Check out what I got for you today!</p>
                    <table style="border: 1px solid white; border-collapse: collapse; margin: 0 auto; text-align: left; background-color: coral;">
                        <tr>
                            <td style="border: 1px solid white; border-collapse: collapse;">Name</td>
                            <td style="border: 1px solid white; border-collapse: collapse;">Price</td>
                            <td style="border: 1px solid white; border-collapse: collapse;">Discount</td>
                            <td style="border: 1px solid white; border-collapse: collapse;">Lowest price</td>
                            <td style="border: 1px solid white; border-collapse: collapse;">Comment</td>
                        </tr>
    ''' % receiver_name

    email_msg = MIMEMultipart()
    email_msg['Subject'] = f"Steam Deals"
    email_msg['From'] = sender
    email_msg['To'] = receiver_email

    with open(f"out/{save_name}_{n}.json", 'rb') as f:
        old_datas = json.load(f)
        f.close()

    with open(f"out/{temp_name}_{n}.json", 'rb') as f:
        new_datas = json.load(f)
        f.close()

    comments = []

    if len(old_datas['name']) == len(new_datas['name']):
        for i in range(len(old_datas['name'])):
            if new_datas['price'][i] != 0 and old_datas['price'][i] != 0:
                currency_symbol = new_datas['price'][i][0]
                new_price = float(new_datas['price'][i][1:].replace(',', '.'))
                old_price = float(old_datas['price'][i][1:].replace(',', '.'))
                lowest_price = float(old_datas['lowest_price'][i][1:].replace(',', '.'))
                if old_datas['price'][i] != new_datas['price'][i]:
                    new_datas['price'][i] += ' (' + old_datas['price'][i] + ')'
                    if new_price < old_price:
                        if new_price < lowest_price:
                            comments.append(
                                f"You can save {currency_symbol}{round(lowest_price-new_price, 2)} compared to the "
                                f"lowest price.")
                        else:
                            comments.append(
                                f"You can save {currency_symbol}{round(old_price-new_price, 2)} compared to the old "
                                f"price, \nbut you will lose {currency_symbol}{round(new_price-lowest_price, 2)} compared to the"
                                f"lowest price.")
                else:
                    comments.append("Do not buy.")
            else:
                comments.append("No comment.")

    with open(f"out/{temp_name}_{n}.json", 'rb') as f:
        file_attachment = MIMEApplication(f.read())
        f.close()

    shutil.copyfile(f"out/{temp_name}_{n}.json", f"out/{save_name}_{n}.json")

    for i in range(len(new_datas['name'])):
        html += '''\n
                    <tr>
                        <td style="border: 1px solid white; border-collapse: collapse;"><a href=%s>%s</a></td>
                        <td style="border: 1px solid white; border-collapse: collapse;">%s</td>
                        <td style="border: 1px solid white; border-collapse: collapse;">%s</td>
                        <td style="border: 1px solid white; border-collapse: collapse;">%s</td>
                        <td style="border: 1px solid white; border-collapse: collapse;">%s</td>
                    </tr>
        ''' % (f"https://steamdb.info/app/{new_datas['ID'][i]}",
               new_datas['name'][i],
               new_datas['price'][i],
               new_datas['discount'][i],
               new_datas['lowest_price'][i],
               comments[i])

    html += '''\n
                    </table>
                </div>
                <p style="margin: 0;">Thank you for staying with Steam Dealer 666!</p>
                <p style="margin: 0;">Have a good rest of the day!</p>
                <p style="margin: 0;">Byeeee</p>
            </body>
        </html>
    '''

    email_msg.attach(MIMEText(html, "html"))

    file_attachment.add_header("Content-Disposition", f"attachment; filename=games.json")
    email_msg.attach(file_attachment)

    email_string = email_msg.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, receiver_email, email_string)

    print(f"Email sent to {receiver_name}")


url = 'https://steamdb.info/app'

with open('configs/config.json', 'r') as config_file:
    config_data = json.load(config_file)
    config_file.close()

with open('configs/customers.json', 'r') as customers_file:
    customers_data = json.load(customers_file)
    customers_file.close()

sender = config_data['sender']
password = config_data['password']
save_name = config_data['save_name']
temp_name = config_data['temp_name']

api_key = config_data['API_KEY']
user_agent_endpoint = config_data['FAKE_USER_AGENT_ENDPOINT']
browser_header_endpoint = config_data['FAKE_BROWSER_HEADER_ENDPOINT']
proxy_endpoint = config_data['PROXY_ENDPOINT']
num_results = config_data['SCRAPEOPS_NUM_RESULTS']

for i, customer_data in enumerate(customers_data):
    customer_email = customer_data['email']
    customer_name = customer_data['name']
    gameIds = customer_data['games']
    currency = customer_data['currency']

    games = {
        "name": [],
        "ID": [],
        "price": [],
        "discount": [],
        "lowest_price": []
    }
    if customer_data['subscribed']:
        for j, ID in enumerate(gameIds):
            options = webdriver.ChromeOptions()
            # options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument('--disable-dev-shm-usage')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            service = Service('drivers/chromedriver')
            driver = webdriver.Chrome(service=service, options=options)

            stealth(
                driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )

            try:
                time.sleep(random.randint(5, 10))
                driver.get(f'{url}/{ID}/')

                if "Checking your browser" in driver.page_source:
                    time.sleep(random.randint(5, 10))
                    driver.get(f'{url}/{ID}')

                if not os.path.exists("drivers/cookies.pkl"):
                    pickle.dump(driver.get_cookies(), open("drivers/cookies.pkl", "wb"))
                else:
                    cookies = pickle.load(open("drivers/cookies.pkl", "rb"))
                    for cookie in cookies:
                        driver.add_cookie(cookie)

                xpath = "//h1[@itemprop='name']"

                element_present = EC.presence_of_element_located((By.XPATH, xpath))
                WebDriverWait(driver, 100).until(element_present)

                name = ''
                price = ''
                discount = ''
                lowestPrice = ''

                try:
                    # Get a name and an ID
                    xpath = "//h1[@itemprop='name']"
                    name = driver.find_element(By.XPATH, xpath).text
                    time.sleep(random.randint(2, 6))

                    xpath = "//td[@id='js-price-history']"
                    if driver.find_element(By.XPATH, xpath).get_attribute('data-cc') != currency:
                        # Click on prices
                        xpath = "//a[@id='tab-prices']"
                        driver.find_element(By.XPATH, xpath).click()

                        time.sleep(random.randint(2, 6))

                        # Click on currency
                        xpath = "//button[@id='js-currency-selector']"
                        driver.find_element(By.XPATH, xpath).click()

                        time.sleep(random.randint(2, 6))

                        # Select currency
                        xpath = f"//button[@data-cc='{currency}']"
                        driver.find_element(By.XPATH, xpath).click()

                        time.sleep(random.randint(2, 6))

                    # Get current price
                    xpath = "//tr[@class='table-prices-current']//td[@id='js-price-history']/following-sibling::td"
                    price = driver.find_element(By.XPATH, xpath).text

                    if len(price.split(' ')) > 1:
                        discount = price.split(' ')[-1]
                        price = price.split(' ')[0]

                    price = 0 if price == 'N/A' else price

                    # Get the lowest price
                    xpath = "//tr[@class='table-prices-current']//td[@id='js-price-history']/following-sibling::td[3]"
                    lowestPrice = driver.find_element(By.XPATH, xpath).text

                except NoSuchElementException:
                    price = 0

                games['name'].append(name)
                games['ID'].append(ID)
                games['price'].append(price)
                games['discount'].append(discount)
                games['lowest_price'].append(lowestPrice)

            except TimeoutException:
                print("Time out exception")
                exit()

            driver.close()

        if not os.path.exists(f"out/{save_name}_{i}.json"):
            with open(f"out/{save_name}_{i}.json", "w") as outfile:
                json.dump(games, outfile)

        with open(f"out/{temp_name}_{i}.json", "w") as outfile:
            json.dump(games, outfile)

        send_email(i, sender, password, customer_email, customer_name, save_name)

    else:
        print(f"{customer_name} is not subscribed, what a pity.")
