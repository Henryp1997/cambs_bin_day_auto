from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import smtplib
import os

def main():
    """ get the next bin which is to be left out for collection
        and the corresponding collection date """
    
    # directory of this file
    global_dir = f"{os.path.dirname(os.path.realpath(__file__))}"

    # website with bin day information
    bin_day_url = read_config("bin_day_url")

    # user's post code and address
    post_code = read_config("post_code")
    address = read_config("address")

    # firefox browser object
    service = Service(f"{global_dir}/drivers/geckodriver.exe")
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument("--headless=new")
    firefox_options.binary_location = read_config("firefox_path")
    browser = webdriver.Firefox(service=service, options=firefox_options)

    # get bin collection dates
    bin_dict = get_bin_day_info(browser, bin_day_url, post_code, address)

    # email result to given email address
    user_gmail = read_config("user_gmail")
    user_receive = read_config("user_receive")
    gmail_app_passwd = read_config("gmail_app_passwd")
    send_bin_dates_to_email(user_gmail, user_receive, gmail_app_passwd, bin_dict)

    # exit firefox instance
    browser.quit()

def get_bin_day_info(browser, bin_day_url, post_code, address, timeout=5):
    browser.get(bin_day_url)

    # wait for cookies pop-up to appear and record the ID of the Deny button. Then click button
    cookie_deny_btn = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.ID, "CybotCookiebotDialogBodyButtonDecline")))
    browser.execute_script('arguments[0].click()', cookie_deny_btn)

    # find post code field then enter post code
    post_code_field = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.ID, "postcode")))
    post_code_field.send_keys(post_code)

    # press enter to search for post code
    post_code_field.send_keys(Keys.ENTER)

    # now search through the address list to find the user's address
    address_list = WebDriverWait(browser, timeout).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "list-group-item")))
    for add in address_list:
        add_contents = add.get_attribute("innerHTML")
        if address.lower() in add_contents:
            break

    # click the link corresponding to the correct address
    browser.execute_script('arguments[0].click()', add)

    # get divs with each bin colour's next collection dates
    bin_day_list_items = WebDriverWait(browser, timeout).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tick-sm")))

    # find order of bins presentation on page, just in case it ever changes
    bin_dict = {}
    for i, info in enumerate(bin_day_list_items):
        if i > 2:
            break
        bin_colour = (info.get_attribute('src').split("collection-")[1].split("png")[0].strip("."))
        bin_dict[f"bin_{i}"] = (bin_colour, "")
    
    # now get the bin day info div and find the <strong> tags, which contain the dates
    bin_dates = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.ID, "refuseCollectionInfo")))
    date_objs = bin_dates.find_elements(By.TAG_NAME, "strong")

    for i, date_obj in enumerate(date_objs):
        date = date_obj.get_attribute('innerHTML')
        bin_dict[f"bin_{i}"] = (bin_dict[f"bin_{i}"][0], date)
    
    return bin_dict

def send_bin_dates_to_email(user_gmail, user_main, gmail_app_passwd, bin_dict):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(user_gmail, gmail_app_passwd)

    # get next bin from dict and current date
    message = get_next_bin(bin_dict)

    server.sendmail(user_gmail, user_main, message)

def get_next_bin(bin_dict):    
    date_format = "%A %d %B %Y"
    black_date = datetime.strptime(bin_dict['bin_0'][1], date_format)
    blue_green_date = datetime.strptime(bin_dict['bin_1'][1], date_format)
    
    bin_options = ["Black", "Blue and green"]
    bin_dates = [black_date, blue_green_date]

    next_bin_date = min(black_date, blue_green_date)
    next_bin = bin_options[bin_dates.index(next_bin_date)]

    # now that we have the next bin date, we need to make sure it isn't past that date already
    today = datetime.now()

    # after 7am on the day of collection
    if ((today - next_bin_date).seconds) / 3600 > 7:
        index = bin_options.index(next_bin) - 1
        next_bin = bin_options[index]
        next_bin_date = bin_dates[index]

    return f"Next bin = {next_bin}, collection date is {next_bin_date.strftime(date_format)}"
            
def read_config(string):
    with open(f'{os.path.dirname(os.path.realpath(__file__))}/config.txt', 'r') as f:
        params = f.readlines()
    
    return [i.split(" = ")[1] for i in params if string in i][0].strip("\n")

if __name__ == "__main__":
    main()
    