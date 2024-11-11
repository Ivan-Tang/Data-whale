import pandas as pd 
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
base_path = Path(os.path.dirname(os.path.abspath(__file__)))
weather_info = pd.read_csv(base_path/'data'/'weatherinfo.csv', index_col=0)
electricity_price = pd.read_csv(base_path/'data'/'electricity_price.csv', index_col=0)


# 调整索引的命名
weather_info.index.rename('Date', inplace=True)
electricity_price.index.rename('DateTime', inplace=True)

electricity_price.index = pd.to_datetime(electricity_price.index)

# 然后，将索引格式化为'2021-01-01'的格式
electricity_price.index = electricity_price.index.strftime('%Y-%m-%d')

print(electricity_price.head())

# 按照日期分组，并计算demand和clearing price的平均值
daily_avg = electricity_price.groupby(electricity_price.index).agg({
    'demand': 'mean',
    'clearing price (CNY/MWh)': 'mean'
}).reset_index()

# 重命名列，使它们更易于理解
daily_avg.columns = ['Date', 'AvgDemand', 'AvgClearingPrice']

daily_avg = daily_avg.set_index('Date')

# daily_avg现在包含了每天的demand和clearing price的平均值
print(daily_avg)

df = daily_avg.join(weather_info, how = 'inner')  # 'func' 是一个函数，用于定义如何合并具有相同索引的行

print(df)

# 计算每列NaN值的数量
nan_count_per_column = df.isna().sum()

# 打印结果
print(nan_count_per_column)


# 找出包含NaN值的行
rows_with_nan = df[df.isna().any(axis=1)]

# 打印结果
print(rows_with_nan)

# 将 '-' 转换为 NaN
df['Aircon index'] = df['Aircon index'].replace('-', np.nan)

# 计算列的平均值，这里需要排除 NaN
mean_value = df['Aircon index'].mean()

# 填充 NaN 值
df['Aircon index'].fillna(mean_value, inplace=True)

'''
# 创建一个图形，大小为 8x10 英寸
plt.figure(figsize=(8, 10))

# 绘制回归图（散点图及拟合线）
sns.regplot(
    data=df,  # 选择2022年的数据
    x="AvgDemand",                         # x 轴为平均价格
    y="Wind scale",                          # y 轴为风力
    scatter_kws={                       # 设置散点图的样式
        "s": 0.5,                      # 散点的大小设置为 0.5
        "alpha": 0.6,                  # 散点的透明度设置为 0.6
        "color": "black"               # 散点的颜色设置为黑色
    },
    color="red",                        # 拟合线的颜色设置为红色
    lowess=True                          # 启用局部加权回归（Lowess）以拟合数据
)
'''
