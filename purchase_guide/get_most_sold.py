from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def browser_init():
    window_size = "1920,1080"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=%s" % window_size)
    browser = webdriver.Chrome("chromedriver", chrome_options=chrome_options)
    return browser


# def browser_quit(browser):
#     browser.quit()


# def navigate_website(browser):
#     bl_pg = "https://ci.eu-de-2.cloud.sap/login"
#     browser.get(bl_pg)
#     cc_github_login_btn = browser.find_element_by_xpath(
#         "/html/body/div[2]/div/div/div[1]/a/button"
#     )

#     cookies_list = browser.get_cookies()
#     for cookie in cookies_list:
#         if cookie["name"] != "skymarshal_auth":
#             continue
#         token = cookie.get("value").strip("/n").strip('"').replace("Bearer ", "")
#     return token


def main():
    # r = requests.get("https://www.bricklink.com/catalogStatsSold.asp?itemType={}&v=0".format(type))

    browser = browser_init()


# token = navigate_website(browser)
# write_token_to_file(token)
# browser_quit(browser)


if __name__ == "__main__":
    main()

