# Web scraping to automate checking which bin is next to be left out (Cambridge only)
Scrape the Cambridge government website after inputting cambridge address and post code. Return the bin day information and email to provided email address (requires setting up gmail with Python, needs specific app password)

## Set up
1. Set up an app password with a gmail account - https://support.google.com/mail/answer/185833?hl=en-GB. This is what allows the Python code to send emails using your gmail account. The app password must be entered into the `config.txt` file under `app_password` (leave the spaces in)
2. Fill in the remaining fields in the `config.txt` file. These include the geckodriver (web driver for firefox) path, Firefox install path, post code, address, gmail account (for sending emails) and another email account (for receiving the email):
```plaintext
bin_day_url = https://www.cambridge.gov.uk/check-when-your-bin-will-be-emptied
firefox_path = /usr/bin/firefox
geckodriver_path = /home/user/cambs_bin_day_auto/drivers/geckodriver
post_code = <Post code here>
address = <Address as it appears on the gov website here>
user_gmail = <gmail account to send emails>
user_receive = <email account to receive emails>
gmail_app_passwd = xxxx xxxx xxxx xxxx
```

## How to use
Run the script: `python3 bin_day.py`. This will scrape the gov website and find out the correct bin day for your given post code and address. You may want to set this up on a crontab in Linux. For example, I have it set up to run every Monday at 5pm (because the bins are collected on Tuesday in my area):
```shell
# in crontab (to get here: crontab -e)
0 17 * * 6 ~/cambs_bin_day_auto/bin/python ~/cambs_bin_day_auto/bin_day.py
```
