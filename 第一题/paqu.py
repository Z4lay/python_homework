import requests
import pandas as pd
from time import sleep
import random

# 初始化所有数据列表（放在循环外部）
Fullname_Cn_list = []  # 全名_中文
Fullname_En_list = []  # 全名_英文
Age_list = []  # 年龄
BirthPlace_Cn_list = []  # 出生地_中文
BirthPlace_En_list = []  # 出生地_英文
Gender_list = []  # 性别
Photo_list = []  # 照片
ComName_Cn_list = []  # 公司名称_中文
ComName_En_list = []  # 公司名称_英文
ComHeadquarters_Cn_list = []  # 公司总部地_中文
ComHeadquarters_En_list = []  # 公司总部地_英文
Industry_Cn_list = []  # 所在行业_中文
Industry_En_list = []  # 所在行业_英文
Ranking_list = []  # 排名
Ranking_Change_list = []  # 排名变化
Relations_list = []  # 组织结构
Wealth_list = []  # 财富值_人民币_亿
Wealth_Change_list = []  # 财富值变化
Wealth_USD_list = []  # 财富值_美元
Year_list = []  # 年份

# 循环请求1-6页
for page in range(1, 7):
    sleep_seconds = random.uniform(1, 2)
    print('开始等待{}秒'.format(sleep_seconds))
    sleep(sleep_seconds)
    print('开始爬取第{}页'.format(page))
    offset = (page - 1) * 200
    url = 'https://www.hurun.net/zh-CN/Rank/HsRankDetailsList?num=ODBYW2BI&search=&offset={}&limit=200'.format(offset)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'accept-encoding': 'gzip, deflate, br',
        'content-type': 'application/json',
        'referer': 'https://www.hurun.net/zh-CN/Rank/HsRankDetails?pagetype=rich'
    }

    r = requests.get(url, headers=headers)
    json_data = r.json()

    print("开始解析json数据")
    item_list = json_data['rows']
    for item in item_list:
        # 打印当前处理的人物中文名（可选）
        # print(item['hs_Character'][0]['hs_Character_Fullname_Cn'])

        # 将每页数据添加到总列表中
        Fullname_Cn_list.append(item['hs_Character'][0]['hs_Character_Fullname_Cn'])
        Fullname_En_list.append(item['hs_Character'][0]['hs_Character_Fullname_En'])
        Age_list.append(item['hs_Character'][0]['hs_Character_Age'])
        BirthPlace_Cn_list.append(item['hs_Character'][0]['hs_Character_BirthPlace_Cn'])
        BirthPlace_En_list.append(item['hs_Character'][0]['hs_Character_BirthPlace_En'])
        Gender_list.append(item['hs_Character'][0]['hs_Character_Gender'])
        Photo_list.append(item['hs_Character'][0]['hs_Character_Photo'])
        ComName_Cn_list.append(item['hs_Rank_Rich_ComName_Cn'])
        ComName_En_list.append(item['hs_Rank_Rich_ComName_En'])
        ComHeadquarters_Cn_list.append(item['hs_Rank_Rich_ComHeadquarters_Cn'])
        ComHeadquarters_En_list.append(item['hs_Rank_Rich_ComHeadquarters_En'])
        Industry_Cn_list.append(item['hs_Rank_Rich_Industry_Cn'])
        Industry_En_list.append(item['hs_Rank_Rich_Industry_En'])
        Ranking_list.append(item['hs_Rank_Rich_Ranking'])
        Ranking_Change_list.append(item['hs_Rank_Rich_Ranking_Change'])
        Relations_list.append(item['hs_Rank_Rich_Relations'])
        Wealth_list.append(item['hs_Rank_Rich_Wealth'])
        Wealth_Change_list.append(item['hs_Rank_Rich_Wealth_Change'])
        Wealth_USD_list.append(item['hs_Rank_Rich_Wealth_USD'])
        Year_list.append(item['hs_Rank_Rich_Year'])

# 循环结束后一次性写入CSV
df = pd.DataFrame({
    '排名': Ranking_list,
    '排名变化': Ranking_Change_list,
    '全名_中文': Fullname_Cn_list,
    '全名_英文': Fullname_En_list,
    '年龄': Age_list,
    '出生地_中文': BirthPlace_Cn_list,
    '出生地_英文': BirthPlace_En_list,
    '性别': Gender_list,
    '照片': Photo_list,
    '公司名称_中文': ComName_Cn_list,
    '公司名称_英文': ComName_En_list,
    '公司总部地_中文': ComHeadquarters_Cn_list,
    '公司总部地_英文': ComHeadquarters_En_list,
    '所在行业_中文': Industry_Cn_list,
    '所在行业_英文': Industry_En_list,
    '组织结构': Relations_list,
    '财富值_人民币_亿': Wealth_list,
    '财富值变化': Wealth_Change_list,
    '财富值_美元': Wealth_USD_list,
    '年份': Year_list
})

# 使用'mode=w'覆盖写入，header=True包含列名
df.to_csv('2024胡润百富榜.csv', index=False, header=True, encoding='utf_8_sig')
print("数据已保存至2024胡润百富榜.csv")

import pandas as pd

# 读取数据集
df = pd.read_csv('./2024胡润百富榜.csv')


# 清洗财富值列 - 确保转换为数值类型
def clean_wealth_value(value):
    # 如果已经是数值类型，直接返回
    if isinstance(value, (int, float)):
        return value

    # 处理字符串类型
    if isinstance(value, str):
        # 移除逗号、货币符号等非数字字符（保留小数点）
        cleaned = ''.join(char for char in value if char.isdigit() or char == '.')
        try:
            return float(cleaned)
        except:
            return 0.0  # 转换失败时返回0
    return value  # 其他类型直接返回


# 应用清洗函数
df['财富值_人民币_亿'] = df['财富值_人民币_亿'].apply(clean_wealth_value)
# 将行业数据拆分为多个列
df['行业'] = df['所在行业_中文'].str.split('、')
# 创建一个新的数据帧，每个行业作为一行数据
industry_df = pd.DataFrame({
    '富豪姓名': df['全名_中文'],
    '公司总部地': df['公司总部地_中文'],
    '财富值': df['财富值_人民币_亿']
})
# 遍历每一行，将每个富豪的每个行业拆分为多行数据
rows = []
for _, row in df.iterrows():
    industries = row['行业']
    for industry in industries:
        new_row = {
            '富豪姓名': row['全名_中文'],
            '公司总部地': row['公司总部地_中文'],
            '财富值': row['财富值_人民币_亿'],
            '行业': industry
        }
        rows.append(new_row)
# 创建包含拆分后行业数据的新数据帧
expanded_industry_df = pd.DataFrame(rows)
# 统计每个行业的富豪数量
industry_counts = expanded_industry_df['行业'].value_counts()
# 统计每个行业的财富值总和
industry_wealth_sum = expanded_industry_df.groupby('行业')['财富值'].sum().rename('财富总和(亿)')

# 统计每个行业的平均财富值
industry_wealth_avg = expanded_industry_df.groupby('行业')['财富值'].mean().rename('平均财富(亿)')

# 统计每个行业的中位数财富值
industry_wealth_median = expanded_industry_df.groupby('行业')['财富值'].median().rename('财富中位数(亿)')
# 合并所有统计结果
industry_stats = pd.concat([
    industry_counts,
    industry_wealth_sum,
    industry_wealth_avg,
    industry_wealth_median
], axis=1)
# 打印行业和对应的富豪数量
print(industry_stats.head(20))