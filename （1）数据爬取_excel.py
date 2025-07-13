import requests
from bs4 import BeautifulSoup
import re
import time
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from datetime import datetime


class DalianWeatherScraper:
    def __init__(self):# 是Python中用于对象初始化的方法，当创建类的新实例时，
                        # Python会自动调用这个方法。它的主要作用是为新创建的对象设置初始状态
        self.base_url = "https://www.tianqihoubao.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        '''创建一个持久化的会话对象,与直接使用 
        requests.get()/requests.post() 相比有显著优势:
        TCP连接复用：
        1.保持底层TCP连接打开，避免为每个请求重新建立连接
        对于向同一主机发送多个请求时，性能提升显著
        跨请求保持状态：
        2.自动处理cookies，保持登录状态
        保持认证信息、代理配置等
        3.共享配置：
        可以设置会话级别的headers、auth、超时等参数
        //如果没有这行代码：
        每次请求都需要单独创建新连接，性能较低
        无法自动保持cookies和会话状态
        需要为每个请求单独配置headers等参数
        '''
        self.session.headers.update(self.headers)#将之前定义的headers应用到整个session
        '''如果没有这行代码：
            每次发起请求都需要手动添加headers：
            response = requests.get(url, headers=self.headers)
        '''

    def get_monthly_links(self, start_year=2022, end_year=2024):
        """获取2022-2024年每月天气页面的链接"""
        monthly_links = []

        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                month_str = f"{year}{month:02d}"
                ''' 
                    02d:当 month = 1 → "01"
                        当 month = 9 → "09"
                        当 month = 12 → "12"
                '''
                monthly_links.append(f"/lishi/dalian/month/{month_str}.html")
                '''
                    最后以列表形式返回：
                    [
                    "/lishi/dalian/month/202201.html",  # 2022年1月
                    "/lishi/dalian/month/202202.html",  # 2022年2月
                    "/lishi/dalian/month/202203.html",  # 2022年3月
                    "/lishi/dalian/month/202204.html",  # 2022年4月
                    ………]
                '''
        return monthly_links

    def parse_weather_table(self, html_content, year_month):
        """解析天气表格数据"""
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table')

        if not table:
            print("未找到天气数据表格")
            return []

        data = []
        for row in table.find_all('tr')[1:]:  # 跳过表头行
            cols = row.find_all('td')
            '''
            find_all('tr')[1:]跳过表格的第一行（通常是表头）
            获取每行中的所有<td>单元格
            '''

            if len(cols) < 4 or not cols[0].get_text(strip=True):
                continue
            #表格列数小于四或者存在所提取的文本为空的情况，跳过
            try:
                date_str = cols[0].get_text(strip=True)# 提取第1列的文本并去除首尾空格
                match = re.search(r'(\d{1,2})月(\d{1,2})日', date_str)
                #(\d{1,2}):匹配 1~2位数字，并捕获为分组
                if not match:
                    continue

                month = int(match.group(1))
                day = int(match.group(2))
                #分别对应正则表达式里 第一个括号 和 第二个括号 捕获的内容
                year = int(year_month[:4]) # 从"202301"中提取2023

                try:
                    date = datetime(year, month, day).strftime('%Y-%m-%d')
                except ValueError:
                    continue

                weather = cols[1].get_text(strip=True)
                day_weather, night_weather = weather.split('/') if '/' in weather else (weather, weather)
                #(weather, weather):即原字符串重复两次的元组,即为使用相同值
                #weather.split('/'):将字符串 weather 按照 斜杠 / 进行分割，返回一个 分割后的列表
                ''' 
                weather = "晴/多云/雨"
                result = weather.split('/')
                print(result)
                
                ['晴', '多云', '雨']
                '''
                temp = cols[2].get_text(strip=True)
                temp_nums = re.findall(r'-?\d+', temp)
                '''
                re.findall() 的行为:会扫描整个字符串，找到所有符合模式的子串
                    
                    字符串: 5 ℃   /   - 2 ℃
                           │      │    │
                    匹配:  "5"   跳过  "-2" 
                '''
                #-? 表示可选负号，\d+ 匹配 1 个或多个数字
                #re.findall():返回所有匹配的子字符串列表
                if len(temp_nums) < 2:
                    continue
                high_temp, low_temp = temp_nums[0], temp_nums[1]

                # 提取风力风向
                wind = cols[3].get_text(strip=True)
                day_wind, night_wind = wind.split('/') if '/' in wind else (wind, wind)

                data.append({
                    '日期': date,
                    '白天天气': day_weather.strip(),
                    '夜晚天气': night_weather.strip(),
                    '最高温度': high_temp,
                    '最低温度': low_temp,
                    '白天风力': day_wind.strip(),
                    '夜晚风力': night_wind.strip()
                })

            except Exception as e:
                print(f"处理行时出错: {e}")
                continue

        return data

    def scrape_month(self, month_link):
        """爬取单个月份的天气数据"""
        url = f"{self.base_url}{month_link}"
        print(f"正在爬取: {url}")

        try:
            response = self.session.get(url)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}")
                return []

            # 从URL中提取年月信息（如202201）
            year_month = month_link.split('/')[-1].replace('.html', '')
            '''
                假设 month_link 是：
                "/lishi/dalian/month/202201.html"
                
                split('/')
                用斜杠 / 分割字符串，得到一个列表：
                ['', 'lishi', 'dalian', 'month', '202201.html']
                
                [-1]
                取列表的最后一项（即文件名部分）：
                "202201.html"
                
                replace('.html', '')
                去掉 .html 后缀，最终得到：
                "202201"
                '''

            return self.parse_weather_table(response.text, year_month)

        except Exception as e:
            print(f"爬取 {url} 时出错: {e}")
            return []

    def scrape_all_data(self, start_year=2022, end_year=2024):
        """爬取所有月份的数据"""
        monthly_links = self.get_monthly_links(start_year, end_year)
        all_data = []

        # 使用线程池提高爬取速度
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = executor.map(self.scrape_month, monthly_links)
            for result in results:
                all_data.extend(result)
                #它和 append 方法不同，append 是添加整个对象作为单个元素，而 extend 是展开可迭代对象并合并元素。
                time.sleep(1)  # 礼貌性延迟，避免被封

        return all_data

    def save_to_excel(self, data, filename="dalian_weather_2022-2024.xlsx"):
        """将数据保存到Excel文件"""
        if not data:
            print("没有数据可保存")
            return

        df = pd.DataFrame(data)#使用pandas将Python字典列表转换为DataFrame

        # 确保日期列存在
        if '日期' not in df.columns:
            print("数据中没有日期列")
            return

        # 按日期排序
        df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
        #原始数据中的日期可能是字符串类型，无法正确排序
        df = df.dropna(subset=['日期'])#删除日期列中包含NaT（无效日期）的行
        df = df.sort_values('日期')

        # 保存到Excel
        df.to_excel(filename, index=False)
        print(f"数据已保存到 {filename}")
        print(f"共保存了 {len(df)} 条记录")

    def run(self):
        """运行爬虫"""
        print("开始爬取大连2022-2024年天气数据...")
        weather_data = self.scrape_all_data()
        print(f"共爬取到 {len(weather_data)} 条天气记录")

        if weather_data:
            self.save_to_excel(weather_data)
        else:
            print("没有爬取到任何数据")


if __name__ == "__main__":
    scraper = DalianWeatherScraper()
    scraper.run()#scraper是爬虫实例对象