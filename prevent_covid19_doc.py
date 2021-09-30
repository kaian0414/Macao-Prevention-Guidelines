import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import datetime

# information for sending email
DOMAIN = [YOUR DOMAIN]
API_KEY= [YOUR KEY]
FROM = [FROM EMAIL]
TO = [TO EMAIL]

def send_simple_message(content, subject="Yeah"):
    return requests.post(
        f"https://api.mailgun.net/v3/{DOMAIN}/messages",
        auth=("api", API_KEY),
        data={"from": FROM,
        "to": TO,
        "subject": subject,
        "text": content})

# Today
today_orig = datetime.datetime.today()
today = today_orig.strftime('%d/%m/%Y')
today_doc = today_orig.strftime('%d%m%Y')

# 2020年12月23日發佈了很多指引，以下日期用作testing
today = '23/12/2020'
today_doc = '23122020'


options = Options()
browser = webdriver.Chrome('./chromedriver.exe', options=options)

browser.get('https://www.ssm.gov.mo/apps1/PreventCOVID-19/ch.aspx#clg17458')
time.sleep(1.5)

close_wins = browser.find_element_by_css_selector('button').click()
nav = browser.find_elements_by_class_name('list-group')

time.sleep(1)

# click '防疫指引'
for item in nav:
    if '防疫指引' in item.text:
        item.click()

time.sleep(2)

# 是日新措施
today_guidelines = []

# 政府部門及公共設施
print('** Getting... 政府部門及公共設施 **')
table_gov = browser.find_element_by_id('grid_17674')
gov_data = table_gov.find_elements_by_css_selector('tr') # 標題 + 日期
link_gov = table_gov.find_elements_by_css_selector('a') # 為了get_attribute('href')

gov_list = [] # 儲存每一指引及link

for i in link_gov: # doc names
    for j in gov_data: # doc names with date
        if i.text in j.text: # 如超連結的文件也在指引標題中，則而者為同一項目
            gov_list.append(j.text) # 標題 + 日期
            gov_list.append(i.get_attribute('href')) # link

# 儲存在list中的形式是['標題 日期', 'link', '標題 日期', 'link', ...]
# 需要為它們分組成每2個一組, 即[['標題 日期', 'link'], ['標題 日期', 'link'], ...]

# 分組, 儲存到edu_group
step = 2
gov_group = [gov_list[i:i+step] for i in range(0, len(gov_list), step)]

# 與today有關的儲存至today_guidelines
for each in gov_group:
    if today in each[0]: # each[0]是標題 日期, each[1]是link
        today_guidelines.append(each)

# 教育場所及社會住宿設施
print('** Getting... 教育場所及社會住宿設施 **')
table_edu = browser.find_element_by_id('grid_17676')
edu_data = table_edu.find_elements_by_css_selector('tr')
link = table_edu.find_elements_by_css_selector('a')

edu_list = []

for i in link: # doc names
    for j in edu_data: # doc names with date
        if i.text in j.text:
            edu_list.append(j.text)
            edu_list.append(i.get_attribute('href'))

# 分組
step = 2
edu_group = [edu_list[i:i+step] for i in range(0, len(edu_list), step)]

# today有關
for each in edu_group:
    if today in each[0]:
        today_guidelines.append(each)

print('*' * 20)
num_guidelines = len(today_guidelines)

# 將今日的指引及link用指定寫法save到results
results = []
for i in today_guidelines:
    results.append(f'{(i[0].split(" "))[0]}, 有關文件: {i[1]}\n')

# print是日資訊
print(f'今日公佈了{num_guidelines}個防疫指引')
for res in results:
    print(res)

# 有新指引才發email及儲存
if num_guidelines > 0:
    # send email
    email_content = '\n'.join(results)
    email_subject = f'{today_doc}_公佈了{num_guidelines}個防疫指引'
    send_simple_message(content=email_content, subject=email_subject)

    # save txt
    w_file = open(f'./{today_doc}.txt', 'w', encoding='utf-8')
    w_file.write(f'{today}公佈了{num_guidelines}個防疫指引' + '\n')
    w_file.writelines(results)
    w_file.close()