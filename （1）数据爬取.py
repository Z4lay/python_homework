import requests
from bs4 import BeautifulSoup
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime


class DalianWeatherScraper:
    def __init__(self):
        self.base_url = "https://www.tianqihoubao.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_monthly_links(self, start_year=2022, end_year=2024):
        """获取2022-2024年每月天气页面的链接"""
        monthly_links = []

        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                month_str = f"{year}{month:02d}"
                monthly_links.append(f"/lishi/dalian/month/{month_str}.html")

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

            # 数据有效性检查
            if len(cols) < 4 or not cols[0].get_text(strip=True):
                continue

            try:
                # 提取日期
                date_str = cols[0].get_text(strip=True)
                match = re.search(r'(\d{1,2})月(\d{1,2})日', date_str)
                if not match:
                    continue

                month = int(match.group(1))
                day = int(match.group(2))

                # 从URL中获取年份
                year = int(year_month[:4])

                # 创建标准日期格式
                try:
                    date = datetime(year, month, day).strftime('%Y-%m-%d')
                except ValueError:
                    # 处理无效日期（如2月30日）
                    continue

                # 提取天气状况
                weather = cols[1].get_text(strip=True)
                day_weather, night_weather = weather.split('/') if '/' in weather else (weather, weather)

                # 提取温度
                temp = cols[2].get_text(strip=True)
                temp_nums = re.findall(r'-?\d+', temp)
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
                time.sleep(1)  # 礼貌性延迟，避免被封

        return all_data

    def print_results(self, data):
        """直接打印爬取结果"""
        if not data:
            print("没有数据可显示")
            return

        print("\n大连2022-2024年天气数据：")
        print("=" * 80)
        print(
            f"{'日期':<12}{'白天天气':<10}{'夜晚天气':<10}{'最高温度':<8}{'最低温度':<8}{'白天风力':<15}{'夜晚风力':<15}")
        print("-" * 80)

        for day in sorted(data, key=lambda x: x['日期']):
            print(f"{day['日期']:<12}{day['白天天气']:<10}{day['夜晚天气']:<10}"
                  f"{day['最高温度']:<8}{day['最低温度']:<8}"
                  f"{day['白天风力']:<15}{day['夜晚风力']:<15}")

        print("=" * 80)
        print(f"共显示 {len(data)} 条天气记录")

    def run(self):
        """运行爬虫"""
        print("开始爬取大连2022-2024年天气数据...")
        weather_data = self.scrape_all_data()

        if weather_data:
            self.print_results(weather_data)
        else:
            print("没有爬取到任何数据")


if __name__ == "__main__":
    scraper = DalianWeatherScraper()
    scraper.run()