import os
import time

from utils import print_json

import onetimepass as otp
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import BaseWebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from dotenv import load_dotenv

load_dotenv()

def keep_trying(callback, max_retries = 10, retry_interval = 1) -> list[Exception]:
  executed = False
  try_count = 0

  exceptions = []

  while not executed and try_count < max_retries:
    try:
      callback()
      executed = True
    except Exception as ex:
      exceptions.append(ex)
    finally: try_count += 1

    time.sleep(retry_interval)

  if not executed:
    raise Exception(exceptions)

  return exceptions

def get_portal_otp() -> str:
  browser_driver: BaseWebDriver = None

  try:

    portal_url = 'https://apontamentos.lab2dev.com/'
    outlook_url = 'https://outlook.office.com/mail/'

    user_email = os.environ['LAB2DEV_USER_EMAIL']
    user_password = os.environ['LAB2DEV_USER_PASSWORD']
    outlook_mfa_secret = os.environ['LAB2DEV_OUTLOOK_MFA_SECRET']

    print(f"mfa: {str(otp.get_totp(outlook_mfa_secret)).rjust(6, '0')}")

    browser_options = webdriver.ChromeOptions()
    browser_options.add_argument("--headless=new")
    browser_options.add_argument("--no-sandbox")
    browser_options.add_argument("--disable-dev-shm-usage")
    browser_options.add_experimental_option("detach", True)
    browser_options.binary_location = "/usr/bin/chromium-browser"

    browser_driver = webdriver.Chrome(
      options=browser_options,
    )

    browser_driver.get(portal_url)

    portal_email_input = WebDriverWait(browser_driver, 30).until(
      expected_conditions.presence_of_element_located((
        By.CSS_SELECTOR,
        'input[type=email]',
      ))
    )

    portal_email_input.clear()
    portal_email_input.send_keys(user_email)
    portal_email_input.send_keys(Keys.RETURN)

    WebDriverWait(browser_driver, 30).until(
      expected_conditions.element_to_be_clickable((
        By.CSS_SELECTOR, 'button[type=submit]',
      ))
    )

    portal_tab_handle = browser_driver.current_window_handle
    browser_driver.switch_to.new_window('tab')

    browser_driver.get(outlook_url)

    outlook_email_input = WebDriverWait(browser_driver, 30).until(
      expected_conditions.presence_of_element_located((
        By.CSS_SELECTOR,
        'input[name=loginfmt]',
      ))
    )
    
    outlook_email_input.send_keys(user_email + Keys.RETURN)

    outlook_password_input = WebDriverWait(browser_driver, 30).until(
      expected_conditions.presence_of_element_located((
        By.CSS_SELECTOR,
        'input[name=passwd]',
      ))
    )
    outlook_password_input.send_keys(user_password)

    keep_trying(
      lambda: WebDriverWait(browser_driver, 30).until(
        expected_conditions.presence_of_element_located((
          By.CSS_SELECTOR,
          'input[type=submit][data-bind]',
        ))
      ).click()
    )

    WebDriverWait(browser_driver, 30).until(
      expected_conditions.presence_of_element_located((
        By.CSS_SELECTOR,
        '#lightbox input[type=checkbox]',
      ))
    )

    browser_driver.get(outlook_url)

    WebDriverWait(browser_driver, 30).until(
      expected_conditions.presence_of_element_located((
        By.XPATH,
        '//*[contains(text(),"LAB2DEV - Senha de acesso")]'
      ))
    )

    inbox_messages = WebDriverWait(browser_driver, 30).until(
      expected_conditions.presence_of_all_elements_located((
        By.CSS_SELECTOR,
        '#MailList .customScrollBar > div > div:has(*[aria-label])',
      ))
    )

    most_recent_otp_message = [
      message
      for message
      in inbox_messages
      if 'LAB2DEV - Senha de acesso' in message.text
    ][0]
    
    keep_trying(
      lambda: (
        ActionChains(browser_driver)
          .move_to_element(most_recent_otp_message)
          .click(most_recent_otp_message)
          .perform()
      )
    )

    most_recent_otp_message_body = WebDriverWait(browser_driver, 30).until(
      expected_conditions.presence_of_element_located((
        By.CSS_SELECTOR,
        '#UniqueMessageBody',
      ))
    )

    one_time_password = most_recent_otp_message_body.text.split("\n")[3]

    delete_email_button = browser_driver.find_element(
      By.CSS_SELECTOR,
      'button:has(i[data-icon-name=DeleteRegular])',
    )

    delete_email_button.click()

    WebDriverWait(browser_driver, 30).until(
      expected_conditions.presence_of_element_located((
        By.CSS_SELECTOR,
        'button:has(i[data-icon-name=Cancel])',
      ))
    ).click()

    browser_driver.close()
    browser_driver.switch_to.window(portal_tab_handle)
    browser_driver.close()

    return one_time_password
  finally:
    if browser_driver: browser_driver.quit()
