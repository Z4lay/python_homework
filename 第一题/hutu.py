import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import numpy as np
from pyecharts.charts import Geo
from pyecharts import options as opts
from pyecharts.globals import ChartType
import matplotlib as mpl
import warnings

# 忽略警告
warnings.filterwarnings('ignore')

# 设置全局样式
plt.style.use('ggplot')
sns.set_style("whitegrid", {'grid.linestyle': '--', 'grid.alpha': 0.3})
mpl.rcParams['font.family'] = 'SimHei'  # 设置中文字体
mpl.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 读取数据
df = pd.read_csv('2024胡润百富榜.csv')


# 数据清洗函数
def clean_data(df):
    """清洗数据，处理异常值"""
    # 1. 性别数据清洗
    gender_mapping = {
        '先生': '男',
        '女士': '女',
        '男性': '男',
        '女性': '女'
    }
    df['性别'] = df['性别'].replace(gender_mapping)
    df['性别'] = df['性别'].fillna('未知')

    # 2. 年龄数据清洗 - 将非数值转换为NaN
    df['年龄'] = pd.to_numeric(df['年龄'], errors='coerce')

    # 3. 财富数据清洗 - 将非数值转换为NaN
    df['财富值_人民币_亿'] = pd.to_numeric(df['财富值_人民币_亿'], errors='coerce')

    # 4. 出生地数据清洗
    def extract_province(address):
        """从出生地中提取省份"""
        if not isinstance(address, str):
            return None
        # 匹配省份和直辖市
        province_pattern = r'(北京|天津|上海|重庆|河北|山西|辽宁|吉林|黑龙江|江苏|浙江|安徽|福建|江西|山东|河南|湖北|湖南|广东|海南|四川|贵州|云南|陕西|甘肃|青海|台湾|内蒙古|广西|西藏|宁夏|新疆|香港|澳门)'
        match = re.search(province_pattern, address)
        if match:
            return match.group(0)
        return None

    df['省份'] = df['出生地_中文'].apply(extract_province)

    return df


# 清洗数据
df = clean_data(df)

# 1. 年龄分布分析 - 柱状图
plt.figure(figsize=(14, 8))
age_data = df['年龄'].dropna()
bins = range(20, 101, 5)  # 每5岁一个区间
counts, bins, patches = plt.hist(age_data, bins=bins, color='#4B9AC0', edgecolor='white', alpha=0.85)

# 添加数据标签
for i in range(len(patches)):
    if counts[i] > 0:  # 只显示有数据的柱子
        plt.text(patches[i].get_x() + patches[i].get_width() / 2,
                 patches[i].get_height() + 0.5,
                 int(counts[i]),
                 ha='center',
                 fontsize=10)

plt.title('2024胡润百富榜富豪年龄分布', fontsize=18, pad=20)
plt.xlabel('年龄区间', fontsize=14)
plt.ylabel('人数', fontsize=14)
plt.xticks(bins, [f"{i}-{i + 4}岁" for i in bins[:-1]] + ['95+岁'])
plt.tight_layout()
plt.savefig('富豪年龄分布.png', dpi=300, bbox_inches='tight')
plt.show()

# 2. 性别分布分析 - 饼图
plt.figure(figsize=(10, 10))
gender_counts = df['性别'].value_counts()
colors = ['#3498db', '#e74c3c', '#95a5a6']  # 男、女、未知
explode = (0.05, 0.05, 0)  # 突出前两个

wedges, texts, autotexts = plt.pie(
    gender_counts.values,
    labels=gender_counts.index,
    autopct='%1.1f%%',
    colors=colors,
    startangle=90,
    explode=explode,
    shadow=True,
    wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
    textprops={'fontsize': 13}
)

# 设置字体大小和颜色
plt.setp(autotexts, size=14, weight="bold", color='white')
plt.title('2024胡润百富榜性别分布', fontsize=18, pad=20)
plt.savefig('富豪性别分布.png', dpi=300, bbox_inches='tight')
plt.show()
# 3. 出生地分布分析 - 柱状图
plt.figure(figsize=(16, 12))

# 获取省份数据并排序
province_counts = df['省份'].value_counts().head(15).sort_values(ascending=True)

# 创建水平条形图
ax = sns.barplot(
    x=province_counts.values,
    y=province_counts.index,
    palette='Blues_r',  # 从深到浅的蓝色
    orient='h'
)

# 添加数据标签
for i, v in enumerate(province_counts.values):
    ax.text(v + 0.5, i, f"{v}", color='black', va='center', fontsize=12)

plt.title('2024胡润百富榜富豪出生地分布（TOP15省份）', fontsize=20, pad=20)
plt.xlabel('人数', fontsize=16)
plt.ylabel('省份', fontsize=16)
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('出生地分布柱状图.png', dpi=300, bbox_inches='tight')
plt.show()

# 出生地分布分析 - 热力图（使用pyecharts）
province_counts = df['省份'].value_counts().reset_index()
province_counts.columns = ['省份', '数量']

# 创建地理热力图
geo = (
    Geo(init_opts=opts.InitOpts(width='1200px', height='900px', theme='light'))
    .add_schema(
        maptype="china",
        itemstyle_opts=opts.ItemStyleOpts(color="#f7f7f7", border_color="#111")
    )
    .add(
        series_name="富豪数量",
        data_pair=[(prov, count) for prov, count in zip(province_counts['省份'], province_counts['数量'])],
        type_=ChartType.HEATMAP,
        label_opts=opts.LabelOpts(is_show=False),
    )
    .set_series_opts(
        label_opts=opts.LabelOpts(font_size=12, color="rgba(0,0,0,0.7)")
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="2024胡润百富榜出生地分布热力图",
            subtitle="数据来源：胡润百富榜",
            title_textstyle_opts=opts.TextStyleOpts(font_size=22),
            subtitle_textstyle_opts=opts.TextStyleOpts(font_size=16)
        ),
        visualmap_opts=opts.VisualMapOpts(
            min_=0,
            max_=max(province_counts['数量']),
            is_calculable=True,
            orient="horizontal",
            pos_left="center",
            pos_bottom="50px",
            range_color=["#E0ECFF", "#1E90FF", "#0066CC"]
        ),
        tooltip_opts=opts.TooltipOpts(
            formatter="{b}: {c}位富豪",
            background_color="rgba(0,0,0,0.7)",
            border_color="#333",
            textstyle_opts=opts.TextStyleOpts(color="#fff")
        ),
        legend_opts=opts.LegendOpts(is_show=False)
    )
)

# 保存为HTML文件
geo.render("出生地分布热力图.html")
print("热力图已保存为'出生地分布热力图.html'")
# 4. 年龄与财富关系分析
plt.figure(figsize=(16, 10))

# 创建自定义调色板
palette = {
    '男': '#3498db',
    '女': '#e74c3c',
    '未知': '#95a5a6'
}

# 创建散点图
scatter = sns.scatterplot(
    data=df,
    x='年龄',
    y='财富值_人民币_亿',
    hue='性别',
    palette=palette,
    size='财富值_人民币_亿',
    sizes=(30, 600),
    alpha=0.75,
    edgecolor='w',
    linewidth=0.8
)

plt.title('富豪年龄与财富分布', fontsize=20, pad=20)
plt.xlabel('年龄', fontsize=16)
plt.ylabel('财富值(亿人民币)', fontsize=16)
plt.grid(alpha=0.2)

# 添加平均线
mean_age = df['年龄'].mean()
mean_wealth = df['财富值_人民币_亿'].mean()
plt.axvline(mean_age, color='#e74c3c', linestyle='--', alpha=0.7)
plt.axhline(mean_wealth, color='#3498db', linestyle='--', alpha=0.7)
plt.text(mean_age + 1, max(df['财富值_人民币_亿'].dropna()) * 0.9, f'平均年龄: {mean_age:.1f}岁',
         fontsize=14, color='#e74c3c')
plt.text(min(df['年龄'].dropna()) + 5, mean_wealth + 100, f'平均财富: {mean_wealth:.1f}亿',
         fontsize=14, color='#3498db')

plt.legend(title='性别', loc='upper right', fontsize=12, title_fontsize=14)
plt.tight_layout()
plt.savefig('年龄与财富分布.png', dpi=300, bbox_inches='tight')
plt.show()

# 5. 行业分布分析（前15名）
plt.figure(figsize=(16, 12))
industry_counts = df['所在行业_中文'].value_counts().head(15)

# 使用水平条形图
ax = sns.barplot(
    x=industry_counts.values,
    y=industry_counts.index,
    hue=industry_counts.index,  # 修复警告
    palette='viridis',
    legend=False
)

plt.title('富豪所在行业分布(TOP15)', fontsize=20, pad=20)
plt.xlabel('人数', fontsize=16)
plt.ylabel('行业', fontsize=16)

# 添加数据标签
for i, v in enumerate(industry_counts.values):
    ax.text(v + 0.5, i, f"{v}", color='black', va='center', fontsize=12)

plt.tight_layout()
plt.savefig('行业分布.png', dpi=300, bbox_inches='tight')
plt.show()

# 6. 财富分布分析
plt.figure(figsize=(16, 10))
wealth_data = df['财富值_人民币_亿'].dropna()

# 创建财富区间
bins = [0, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
labels = ['<50亿', '50-100亿', '100-200亿', '200-500亿', '500-1000亿', '1000-2000亿', '2000-5000亿', '>5000亿']
wealth_cut = pd.cut(wealth_data, bins=bins, labels=labels, right=False)
wealth_counts = wealth_cut.value_counts().sort_index()

# 创建条形图
ax = sns.barplot(
    x=wealth_counts.index,
    y=wealth_counts.values,
    hue=wealth_counts.index,  # 修复警告
    palette='rocket',
    legend=False
)

plt.title('2024胡润百富榜财富分布', fontsize=20, pad=20)
plt.xlabel('财富区间(人民币)', fontsize=16)
plt.ylabel('人数', fontsize=16)
plt.xticks(rotation=15)

# 在每个柱子上方添加数值标签
for i, v in enumerate(wealth_counts.values):
    ax.text(i, v + 0.5, f"{v}", ha='center', fontsize=12)

plt.tight_layout()
plt.savefig('财富分布.png', dpi=300, bbox_inches='tight')
plt.show()


print("所有分析图表已成功生成并保存！")