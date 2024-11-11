import requests as r
from bs4 import BeautifulSoup as bs
from selenium.webdriver.support.ui import Select
import re
from html import unescape
import pandas as pd
import matplotlib.pyplot as plt
import json

def get_his_weatherinfo(year, month, citycode=53698):
    url = 'https://tianqi.2345.com/Pc/GetHistory'
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Cookie": "Hm_lvt_a3f2879f6b3620a363bec646b7a8bcdd=1722323278; HMACCOUNT=5908790C2E00BA61; Hm_lpvt_a3f2879f6b3620a363bec646b7a8bcdd=1722323288",
        "Host": "tianqi.2345.com",
        "Referer": "https://tianqi.2345.com/wea_history/53698.htm",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "macOS"
    }
    params = {
        'areaInfo[areaId]' : citycode,
        'areaInfo[areaType]' : 2,
        'date[year]' : year,
        'date[month]' : month
    }
    w=r.get(url, headers=headers, params=params)
    if w.status_code == 200:
        #print('Successfully connected! Status code is ',w.status_code,'The coding type of the website is ',w.encoding)
        json_data = json.loads(w.text)
        html_content = json_data['data']
        soup = bs(html_content, 'html.parser')
        get_his_msg(soup,year,month)
        return get_his_table(soup)
    else:
        print('Failed to retrieve the webpage! Status code is ',w.status_code)

def get_his_msg(soup,year,month):
    #提取历史温度信息（总结）
    history_msg = soup.find_all('ul', class_ = "history-msg")
    extracted_numbers = []
    for ul in history_msg:
        li_tags = ul.find_all('li')  # 在每个 'ul' 元素中查找 'li' 标签
        for li in li_tags:
            em_tags = li.find_all('em') # 在每个 'li' 元素中查找 'em' 标签
            # 正则表达式，用于匹配数字
            number_pattern = re.compile(r'\d+')
            # 遍历 ResultSet 并提取数字
            for item in em_tags:
                #先将对象转换为字符串，便于用findall函数查找所需数据
                item_str = str(item)
                # 使用正则表达式查找所有数字
                numbers = number_pattern.findall(item_str)
                # 将找到的数字转换为整数
                extracted_numbers.extend(map(int, numbers))
    

    # 打印提取的数字
    avg_h_temp=extracted_numbers[0]
    avg_l_temp=extracted_numbers[1]
    max_temp=extracted_numbers[2]
    min_temp=extracted_numbers[3]
    avg_aircon_index=extracted_numbers[4]
    best_aircon_index=extracted_numbers[5]
    worst_aircon_index=extracted_numbers[6]    

    print(f'已经提取 {year} 年 {month} 月的天气信息：'
      f'本月的平均高温 {avg_h_temp:.1f} 摄氏度。'
      f'本月的平均低温 {avg_l_temp:.1f} 摄氏度。'
      f'本月的最高气温 {max_temp:.1f} 摄氏度。'
      f'本月的最低气温 {min_temp:.1f} 摄氏度。'
      f'本月的平均空气指数 {avg_aircon_index:.1f}，'
      f'本月的最好空气指数 {best_aircon_index:.1f}，'
      f'本月的最差空气指数 {worst_aircon_index:.1f}。')

    #print('已经提取',year,'年',month,'月的天气信息：'本月的平均高温',avg_h_temp,'摄氏度。 本月的平均低温为',avg_l_temp,'摄氏度。 本月的最高气温为'
    #,max_temp,'摄氏度。 本月的最低气温为',min_temp,'摄氏度。本月的平均空气指数为', avg_aircon_index, '，本月的最好空气指数为', best_aircon_index, '，本月的最差空气指数为', worst_aircon_index, '。')
    #print('The average high temperature of this month is ',avg_h_temp,'degree celsius. The average low temperature of this month is',avg_l_temp,'degree celsius. The highest temperature in this month is'
    #,max_temp,'degree celsius. The lowest temperature in this month is',min_temp,'degree celsius.')    


def get_his_table(soup):
    history_table = soup.find_all('table', class_ = "history-table")
    row_data = []
    for table in history_table:
        tr_tags = table.find_all('tr')
        for tr in tr_tags:
            td_tags = tr.find_all('td')
            #整理提取出来的数据格式
            row_tuple = tuple([clean_string(td.get_text()) for td in td_tags])
            row_tuple = tuple(item for item in row_tuple if item != '~' and item != '')
            row_data.append(row_tuple)
    #去掉空列表
    row_data = [t for t in row_data if bool(t)] 
    df = pd.DataFrame(row_data , columns = ['Date', 'Max temp', 'Min temp', 'Wind scale', 'Aircon index'])
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def clean_string(s):
    s = s.strip()
    s = re.sub(r'[^\x00-\x7F]+', '', s)
    s = unescape(s)
    return s


def create_csv(df):
    #指定CSV文件的名称
    csv_name = 'weatherinfo.csv'

    #将DataFrame写入CSV文件，保存在当前工作目录
    df.to_csv(csv_name, index=False)  #index=False表示不将行索引写入文件

    print('A csv file has been successfully created!')

def create_excel(df):
    #指定Excel文件的名称和工作表名称
    excel_name = 'dataframe.xlsx'
    sheet_name = 'Sheet1'

    # 将DataFrame写入Excel文件
    df.to_excel(excel_name, sheet_name=sheet_name, index=False, engine='openpyxl')

    print('A excel file has been successfully created!')

#获取从2021.12到2024.04的数据
df_202112 = get_his_weatherinfo(2021, 12)

#获取2022年和2023年每个月的数据
df_2022_2023 = [get_his_weatherinfo(year, month) for year in [2022, 2023] for month in range(1, 13)]

#获取2024年1月到4月的数据
df_2024_first4 = [get_his_weatherinfo(2024, i) for i in range(1, 5)]

#合并所有DataFrame
df = pd.concat([
    df_202112,
    *df_2022_2023,
    *df_2024_first4
], ignore_index=True)





