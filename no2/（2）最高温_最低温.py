import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 基础设置
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 数据加载与预处理
df = pd.read_excel('dalian_weather_2022-2024.xlsx')
df['日期'] = pd.to_datetime(df['日期'])
df['月'] = df['日期'].dt.month

# 温度数据处理
df[['最高温度','最低温度']] = df[['最高温度','最低温度']].apply(pd.to_numeric, errors='coerce')
#apply(pd.to_numeric)确保温度列是数值类型
''' 
1.apply 的作用:
    apply 是 Pandas 中用于对 DataFrame 或 Series 的某一轴（行或列）应用函数的通用方法。它的常见用法：
    对列操作：df.apply(func) 默认对每一列应用函数 func。
    对行操作：df.apply(func, axis=1) 对每一行应用函数。
2.apply(pd.to_numeric) 的用途
当 DataFrame 中有多列需要转换为数值类型时，可以通过 apply(pd.to_numeric) 批量处理
        import pandas as pd
        # 示例DataFrame（包含字符串类型的数字）
        df = pd.DataFrame({
            "A": ["1", "2", "3"],
            "B": ["4.1", "5.2", "6.3"]
        })
        # 将所有列转换为数值类型
        df = df.apply(pd.to_numeric)
        print(df.dtypes)
        # 输出:
        # A    int64
        # B    float64
'''
# 计算月平均温度
monthly_avg = df.groupby('月').agg(
    平均最高温度=('最高温度', 'mean'),
    最高温度标准差=('最高温度', 'std'),
    平均最低温度=('最低温度', 'mean'),
    最低温度标准差=('最低温度', 'std')
).reset_index()

# 绘制温度变化图
plt.figure(figsize=(12,6))
sns.lineplot(data=monthly_avg, x='月', y='平均最高温度', color='r', label='平均最高温度')
sns.lineplot(data=monthly_avg, x='月', y='平均最低温度', color='b', label='平均最低温度')
plt.fill_between(monthly_avg['月'],
                 monthly_avg['平均最高温度']-monthly_avg['最高温度标准差'],
                monthly_avg['平均最高温度']+monthly_avg['最高温度标准差'],
                color='r', alpha=0.1)
plt.fill_between(monthly_avg['月'],
                monthly_avg['平均最低温度']-monthly_avg['最低温度标准差'],
                monthly_avg['平均最低温度']+monthly_avg['最低温度标准差'],
                color='b', alpha=0.1)
plt.title('大连市月平均气温变化')
plt.xlabel('月份')
plt.ylabel('温度(℃)')
plt.xticks(range(1,13))
plt.grid(linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()
'''
显示两张图，其中有一张空白的原因：
pandas、matplotlib、seaborn三个库，只能使用其中一个库的方法来绘图，不能混着用
1、纯pandas
        plt.figure(figsize=(12,6))
        monthly_avg.plot(
            x='月', 
            y=['平均最高温度', '平均最低温度'], 
            kind='line',
            title='大连市月平均气温变化',
            xlabel='月份',
            ylabel='温度(℃)'
        )
        plt.xticks(range(1,13))
        plt.grid(linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()  # 只保留一个show
2、纯matplotlib
        plt.figure(figsize=(12,6))
        plt.plot(
            monthly_avg['月'], 
            monthly_avg['平均最高温度'], 
            'r-', 
            label='平均最高温度'
        )
        plt.plot(
            monthly_avg['月'],
            monthly_avg['平均最低温度'],
            'b-',
            label='平均最低温度'
        )
        plt.title('大连市月平均气温变化')
        plt.xlabel('月份')
        plt.ylabel('温度(℃)')
        plt.xticks(range(1,13))
        plt.legend()
        plt.grid(linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show() 
3、纯seaborn
        plt.figure(figsize=(12,6))
        sns.lineplot(
            data=monthly_avg.melt(id_vars='月'),  # 转换为长格式
            x='月',
            y='value',
            hue='variable',
            palette=['r', 'b']
        )
        plt.title('大连市月平均气温变化')
        plt.xlabel('月份')
        plt.ylabel('温度(℃)')
        plt.xticks(range(1,13))
        plt.grid(linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()      
'''
