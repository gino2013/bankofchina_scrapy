from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 創建 Chrome 瀏覽器實例
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("--disable-notifications")  # 禁用瀏覽器通知
driver = webdriver.Chrome(service=service, options=options)

# 訪問網頁
url = "https://srh.bankofchina.com/search/whpj/search_cn.jsp"
driver.get(url)

# 等待 JavaScript 加載完成
time.sleep(5)

# 獲取貨幣選擇下拉菜單
currency_select = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "pjname"))
)

# 循環選擇每種貨幣
currencies = [option.get_attribute("value") for option in currency_select.find_elements(By.TAG_NAME, "option")]
for currency in currencies[1:]:  # 從第二個選項開始，跳過"選擇貨幣"
    # 重新獲取貨幣選擇下拉菜單
    currency_select = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "pjname"))
    )
    # 選擇貨幣
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f"//select[@name='pjname']/option[@value='{currency}']"))
    ).click()
    
    time.sleep(1)  # 等待下拉菜單更新
    
    # 點擊位於 'historysearchform' 表單底下的 'input.search_btn' 按鈕
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "form#historysearchform input.search_btn"))
    )
    search_button.click()

    # 等待 AJAX 請求完成並確認表格出現
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
    )

    # 獲取當前頁面的 HTML 源代碼
    html = driver.page_source

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Find the table containing exchange rates
    table = soup.find('div', class_='BOC_main publish').find('table')

    # Extract data from the table
    rates = []
    for row in table.find_all('tr')[1:]:  # Skip the header row
        cols = row.find_all('td')
        if len(cols) > 1:  # Ensure it's a data row
            rate_data = {
                '货币名称': cols[0].text.strip(),
                '现汇买入价': cols[1].text.strip(),
                '现钞买入价': cols[2].text.strip(),
                '现汇卖出价': cols[3].text.strip(),
                '现钞卖出价': cols[4].text.strip(),
                '中行折算价': cols[5].text.strip(),
                '发布时间': cols[6].text.strip()
            }
            rates.append(rate_data)


    # 打印當前貨幣的匯率數據
    print(f"貨幣: {currency}")
    for rate in rates:
        print(rate)
    print("-" * 50)

# 關閉瀏覽器
driver.quit()
