import os
import time
import random
import re
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt')

def print_current_directory():
    print("当前工作目录:", os.getcwd())

def configure_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--ignore-certificate-errors') 
    options.add_argument('--allow-insecure-localhost')    
    options.add_argument('--enable-logging')             
    options.add_argument('--v=1')                        

    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(100)  
        driver.set_script_timeout(100)    
        return driver
    except WebDriverException as e:
        print(f"WebDriver 初始化失败: {e}")
        exit(1)

def accept_google_privacy(driver):
    try:
        agree_button = driver.find_element(By.XPATH, "//div[contains(text(),'I agree') or contains(text(),'同意')]")
        agree_button.click()
        time.sleep(random.uniform(2, 4))
        print("已接受 Google 的隐私协议。")
    except NoSuchElementException:
        print("没有发现隐私协议弹窗，继续执行。")

def search_google(driver, query):
    try:
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(random.uniform(2, 4))  
        print(f"已搜索关键词: {query}")
    except NoSuchElementException as e:
        print(f"搜索框未找到: {e}")
        driver.quit()
        exit(1)

def navigate_to_starting_page(driver, starting_page):
    current_page = 1
    while current_page < starting_page:
        try:
            next_button = driver.find_element(By.ID, "pnnext")
            next_button.click()
            current_page += 1
            print(f"已导航到第 {current_page} 页。")
            time.sleep(random.uniform(3, 6))  # 等待新页面加载
        except NoSuchElementException:
            print(f"无法导航到第 {current_page + 1} 页。可能已经没有更多页面。")
            break

def extract_links(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    search_results = soup.find_all('div', class_='g')

    links = []
    for result in search_results:
        link_tag = result.find('a', href=True)
        if link_tag:
            href = link_tag['href']
            if href.startswith('http') and not href.startswith('https://webcache.googleusercontent.com'):
                links.append(href)
    return links

def is_valid_link(link):
    parsed = urlparse(link)
    return parsed.scheme in ['http', 'https']

def split_into_sentences(text):
    return sent_tokenize(text)

def check_page_content(driver, required_keywords, optional_keywords):
    try:
        page_element = driver.find_element(By.TAG_NAME, "body")
        page_text = page_element.text.lower()
    except NoSuchElementException:
        page_text = ""

    all_required_present = all(re.search(r'\b' + re.escape(keyword.lower()) + r'\b', page_text) for keyword in required_keywords)
    any_optional_present = any(re.search(r'\b' + re.escape(keyword.lower()) + r'\b', page_text) for keyword in optional_keywords)

    return all_required_present and any_optional_present

def save_links_to_file(links, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        for idx, link in enumerate(links, 1):
            file.write(f"{idx}. {link}\n")
    print(f"符合条件的链接已保存到 '{file_path}'。")

def wait_for_page_load(driver, timeout=20):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except TimeoutException:
        print("页面加载超时。")

def main():
    print_current_directory()
    driver = configure_driver()

    try:
        driver.get("https://www.google.com")
        wait_for_page_load(driver, timeout=30)
        print("已打开 Google 首页。")

        accept_google_privacy(driver)






        search_google(driver, "ammonia leak")
        required_keywords = ["ammonia"]  
        optional_keywords = ["sea","port","shore"]      
        starting_page = 1
        num_pages = 5  
        current_page = starting_page






        navigate_to_starting_page(driver, starting_page)

        matching_links = []

        for _ in range(num_pages):
            print(f"正在处理第 {current_page} 页...")
            time.sleep(random.uniform(2, 4))  

            links = extract_links(driver)
            print(f"第 {current_page} 页找到 {len(links)} 个有效链接。")

            for link in links:
                if link in matching_links:
                    continue  
                if not is_valid_link(link):
                    print(f"跳过无效链接: {link}")
                    continue
                try:
                    print(f"正在检查链接: {link}")
                    driver.execute_script("window.open('');")
                    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(len(driver.window_handles)))
                    driver.switch_to.window(driver.window_handles[-1]) 
                    driver.get(link)
                    wait_for_page_load(driver, timeout=30)  

                    if check_page_content(driver, required_keywords, optional_keywords):
                        print(f"找到匹配链接: {link}")
                        matching_links.append(link)
                    else:
                        print(f"不匹配: {link}")

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(random.uniform(1, 3))
                except (TimeoutException, WebDriverException) as e:
                    print(f"处理链接 {link} 时出错: {e}")
                    try:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    except WebDriverException:
                        pass
                    time.sleep(random.uniform(1, 3))
                except Exception as e:
                    print(f"处理链接 {link} 时遇到未预料的错误: {e}")
                    try:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    except WebDriverException:
                        pass
                    time.sleep(random.uniform(1, 3))

            try:
                next_button = driver.find_element(By.ID, "pnnext")
                next_button.click()
                current_page += 1
                print(f"已导航到第 {current_page} 页。")
                time.sleep(random.uniform(3, 6))  
            except NoSuchElementException:
                print("没有找到下一页按钮或无法点击下一页。")
                break

        print("\n符合条件的链接:")
        for idx, link in enumerate(matching_links, 1):
            print(f"{idx}. {link}")

        output_file = os.path.join(os.getcwd(), "matching_links(op).txt")
        save_links_to_file(matching_links, output_file)

    except Exception as e:
        print(f"发生错误: {e}")

    finally:
        driver.quit()
        print("已关闭浏览器。")

if __name__ == "__main__":
    main()
