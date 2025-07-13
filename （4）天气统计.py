import pandas as pd
import matplotlib.pyplot as plt

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取并处理数据
df = pd.read_excel('dalian_weather_2022-2024.xlsx')
df['白天天气'] = df['白天天气'].str.replace('转.*', '', regex=True)
df['夜晚天气'] = df['夜晚天气'].str.replace('转.*', '', regex=True)
# 使用正则表达式处理天气数据，将"转"字后面的内容去除（如"晴转多云"变为"晴"）
# 对白天和夜晚天气列都进行相同处理
# 统计天气频次
weather_data = pd.concat([
    df['白天天气'].value_counts().rename('白天'),
    df['夜晚天气'].value_counts().rename('夜晚')
], axis=1).fillna(0)

# 取前10种常见天气
top_weather = weather_data.sum(axis=1).nlargest(10).index
weather_data = weather_data.loc[top_weather]

# 绘制图表
ax = weather_data.plot.bar(
    figsize=(12, 6),
    color=['#FFD700', '#4682B4'],
    width=0.8,
    edgecolor='black'
)

# 添加柱顶数值
for p in ax.patches:  # 遍历图形中的所有柱子（矩形条）
    ax.annotate(
        f"{int(p.get_height())}",  # 要显示的文本（柱子高度，转为整数）
        (p.get_x() + p.get_width() / 2., p.get_height()),  # 标签位置（柱子顶部中心）
        ha='center',  # 水平对齐方式：居中
        va='center',  # 垂直对齐方式：居中
        xytext=(0, 5),  # 文本偏移量（向上偏移5个单位）
        textcoords='offset points'  # 偏移单位：点（points）
    )

# 设置图表样式
plt.title('大连市2022-2024年天气状况分布 (前10种)')
plt.xlabel('天气类型')
plt.ylabel('天数')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.4)
plt.tight_layout()
plt.show()