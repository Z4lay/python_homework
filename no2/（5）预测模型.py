import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from xgboost import XGBRegressor

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
df = pd.read_excel('dalian_weather_2022-2024+2025.1-6.xlsx')

# 转换日期并提取年月
df['日期'] = pd.to_datetime(df['日期'])
df['年'] = df['日期'].dt.year
df['月'] = df['日期'].dt.month

# 计算每月平均温度
monthly_temp = df.groupby(['年', '月']).agg({'最高温度': 'mean'}).reset_index()

# 添加时间序号 + 月份特征（让模型知道季节变化）
monthly_temp['时间序号'] = (monthly_temp['年'] - 2022) * 12 + monthly_temp['月']
monthly_temp['月份_sin'] = np.sin(2 * np.pi * monthly_temp['月'] / 12)  # 用sin/cos捕捉周期性
monthly_temp['月份_cos'] = np.cos(2 * np.pi * monthly_temp['月'] / 12)

# 训练数据（2022-2024）
train_data = monthly_temp[monthly_temp['年'] < 2025].copy()
X_train = train_data[['时间序号', '月份_sin', '月份_cos']]  # 加入月份特征
y_train = train_data['最高温度']

# 测试数据（2025年1-6月）
test_data = monthly_temp[(monthly_temp['年'] == 2025) & (monthly_temp['月'] <= 6)].copy()
X_test = test_data[['时间序号', '月份_sin', '月份_cos']]
y_test = test_data['最高温度']

# 训练XGBoost模型（比多项式回归更适合时间序列）
model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
model.fit(X_train, y_train)

# 预测
test_data.loc[:, '预测温度'] = model.predict(X_test)

# 计算MSE
# mse = mean_squared_error(y_test, test_data['预测温度'])
# print(f"模型在测试集上的均方误差(MSE): {mse:.2f}")

# 绘制结果
plt.figure(figsize=(12, 6))
plt.plot(train_data['时间序号'], train_data['最高温度'], 'b-', label='历史真实温度')
plt.plot(test_data['时间序号'], test_data['最高温度'], 'r-', linewidth=2, label='2025真实温度')
plt.plot(test_data['时间序号'], test_data['预测温度'], 'm--', linewidth=2, label='2025预测温度')

plt.title('大连市2025年1-6月最高温度预测 (XGBoost模型)', fontsize=15)
plt.xlabel('时间序号', fontsize=12)
plt.ylabel('平均最高温度(℃)', fontsize=12)
plt.xticks(range(1, 43, 3), [f'{2022+(i-1)//12}年{(i-1)%12+1}月' for i in range(1, 43, 3)], rotation=45)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(fontsize=12)
plt.tight_layout()
plt.show()

# 显示预测对比
print("\n2025年1-6月预测与实际温度对比:")
result = test_data[['年', '月', '最高温度', '预测温度']].copy()
result.loc[:, '误差'] = (result['预测温度'] - result['最高温度']).round(1)
result.columns = ['年', '月', '实际温度', '预测温度', '误差']
print(result.round(1))