import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from matplotlib.ticker import MaxNLocator

plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体为黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 加载数据
df = pd.read_excel('dalian_weather_2022-2024.xlsx')

# 转换日期列为datetime格式
df['日期'] = pd.to_datetime(df['日期'])
df['年份'] = df['日期'].dt.year
df['月份'] = df['日期'].dt.month

# 定义风力等级分类
wind_levels = ['1-2级', '3-4级', '4-5级', '5-6级', '6-7级', '>7级']
colors = ['#66b3ff', '#ff9999', '#99ff99', '#ffcc99', '#cc99ff', '#ff6666']


def classify_wind(wind_str):
    if pd.isna(wind_str):
        return '1-2级'  # 将缺失值归类为1-2级

    if '无持续风向' in wind_str:
        return '1-2级'  # 将无持续风向归类为1-2级

    # 提取数字部分
    match = re.search(r'(\d+)-(\d+)级', wind_str)
    if not match:
        match = re.search(r'(\d+)级', wind_str)
        if match:
            wind_num = int(match.group(1))
        else:
            return '1-2级'
    else:
        wind_num = int(match.group(2))  # 取较高的风力值

    # 分类
    if wind_num <= 2:
        return '1-2级'
    elif wind_num <= 4:
        return '3-4级'
    elif wind_num == 5:
        return '4-5级'
    elif wind_num == 6:
        return '5-6级'
    elif wind_num == 7:
        return '6-7级'
    else:
        return '>7级'


# 应用分类函数
df['风力分类'] = df['白天风力'].apply(classify_wind)

# 按年月统计各风力等级天数
wind_monthly = df.groupby(['年份', '月份', '风力分类']).size().unstack(fill_value=0)
wind_monthly = wind_monthly.reindex(columns=wind_levels, fill_value=0)

# 创建月份标签
month_labels = [f'{y}年{m}月' for y, m in wind_monthly.index]

# 绘制堆叠柱状图
plt.figure(figsize=(18, 8))
ax = plt.gca()

# 每个风力等级的数据
bottom = np.zeros(len(wind_monthly))
for i, level in enumerate(wind_levels):
    ax.bar(month_labels, wind_monthly[level], bottom=bottom,
           label=level, color=colors[i], width=0.8)
    bottom += wind_monthly[level]

# 添加数据标签
for i, month in enumerate(month_labels):
    total = 0
    for level in wind_levels:
        count = wind_monthly[level].iloc[i]
        if count > 0:
            ax.text(i, total + count / 2, str(count),
                    ha='center', va='center', color='white', fontsize=8)
        total += count

# 图表美化
plt.title('大连市2022-2024年各月份风力等级分布', fontsize=16, pad=20)
plt.xlabel('月份', fontsize=13)
plt.ylabel('天数', fontsize=13)
plt.xticks(rotation=45, ha='right')
plt.grid(True, axis='y', linestyle='--', alpha=0.6)
plt.legend(title='风力等级', fontsize=10, title_fontsize=12, bbox_to_anchor=(1.02, 1), loc='upper left')

# 调整y轴刻度为整数
ax.yaxis.set_major_locator(MaxNLocator(integer=True))

plt.tight_layout()
plt.show()