import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from sqlalchemy import create_engine

plt.rcParams["font.sans-serif"] = ["SimHei"] # 显示中文
plt.rcParams["axes.unicode_minus"] = False  # 显示负号


# ===== 配置模块：数据库连接参数与输出目录设置 =====

# 该部分代码（db）为示例配置，运行前请按本地数据库环境修改 port、user、password 等连接参数
db = {
    "host": "localhost",
    "port": "****",  # 端口
    "user": "****",  # 用户名
    "password": "********",  # 密码
    "database": "taobao_analysis",
    "charset": "utf8mb4"
}

output_table_dir = "../output/tables" # 数据表输出路径
output_fig_dir = "../output/figures"  # 图片输出路径

# 创建目录
os.makedirs(output_table_dir, exist_ok=True) 
os.makedirs(output_fig_dir, exist_ok=True)


# ===== 公共函数模块 =====
    
# 连接数据库并读取数据表
def read_table(table_name: str) -> pd.DataFrame:
    url = (
        f"mysql+pymysql://{db['user']}:{db['password']}"
        f"@{db['host']}:{db['port']}/{db['database']}?charset={db['charset']}"
    )
    engine = create_engine(url)
    sql = f"SELECT * FROM {table_name}"
    return pd.read_sql(sql, engine)

# 保存数据表
def save_csv(df: pd.DataFrame, filename: str):
    path = os.path.join(output_table_dir, filename)
    df.to_csv(path, index=False, encoding="utf-8-sig")

# 保存结果图
def save_fig(filename: str):
    path = os.path.join(output_fig_dir, filename)
    plt.tight_layout() # 自动调整子图参数
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


# ====== 分析与可视化模块 ======

# 1.日流量与行为趋势分析

def daily_traffic_analysis():
    df = read_table("ads_daily_traffic").copy()
    
    # 衍生指标
    df["pv_per_uv"] = round(df["pv_count"] / df["uv"].replace(0,np.nan),2)      # 人均浏览量
    df['buy_per_uv'] = round(df['buy_count'] / df['uv'].replace(0, np.nan),2)   #  人均购买量
    df['pv_to_buy_rate'] = round(df['buy_count'] / df['pv_count'].replace(0, np.nan),5)
    df['cart_to_buy_rate'] = round(df['buy_count'] / df['cart_count'].replace(0, np.nan),5)
    df['fav_to_buy_rate'] = round(df['buy_count'] / df['fav_count'].replace(0, np.nan),5)
    # 保存数据表
    save_csv(df, "ads_daily_traffic.csv")
    
    # 创建画布
    fig, ax = plt.subplots(2,1,figsize=(15, 12),sharex=True)
    fig.patch.set_facecolor('white')
    ax[0].set_facecolor('white')
    ax[1].set_facecolor('white')
    
    # 图1（a）：每日流量趋势

    # 由于 PV 与 UV、购买数的量级不同，
    # 为避免共用同一 y 轴时曲线被压扁，这里采用左右双轴展示。
    # 左轴：UV 折线图
    line_uv, = ax[0].plot(
        df['event_date'], df['uv'],
        marker='o', linewidth=2, markersize=5, 
        label='UV'
    )
    # 左轴：购买数柱状图
    bars_buy = ax[0].bar(
        df["event_date"], df["buy_count"],
        width=0.6, alpha=0.35,
        label="购买数"
    )
    
    ax[0].set_title('图1（a）流量与购买趋势', fontsize=14, pad=12)
    ax[0].set_ylabel('UV / 购买数')
    ax[0].grid(True, linestyle='--', alpha=0.3)
    
    # 右轴：PV
    ax1 = ax[0].twinx()
    line_pv, = ax1.plot(
        df['event_date'], df['pv_count'],
        marker='D', linewidth=2, markersize=5, color='r',
        label='PV'
    )
    ax1.set_ylabel('PV')

    # 合并图例
    handles = [line_uv, bars_buy, line_pv]
    labels0 = ["UV", "购买数", "PV"]
    ax[0].legend(handles, labels0, loc='upper left', frameon=False)


    # 图1（b）：每日关键转化率趋势
    line_ptb = ax[1].plot(
        df['event_date'], df['pv_to_buy_rate'],
        marker='o', linewidth=2, markersize=5, label='浏览->购买'
    )
    line_ctb = ax[1].plot(
        df['event_date'], df['cart_to_buy_rate'],
        marker='s', linewidth=2, markersize=5, label='加购->购买'
    )
    line_ftb = ax[1].plot(
        df['event_date'], df['fav_to_buy_rate'],
        marker='d', linewidth=2, markersize=5, label='收藏->购买'
    )

    ax[1].set_title('图1（b）关键转化率趋势', fontsize=14, pad=12)
    ax[1].set_ylabel('转化率')
    ax[1].set_xlabel('日期')
    ax[1].grid(True, linestyle='--', alpha=0.3)
    # y轴以百分号形式显示
    ax[1].yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))

    # 合并图例
    lines = line_ptb + line_ctb + line_ftb
    labels1 = [l.get_label() for l in lines]
    ax[1].legend(lines, labels1, loc='upper left', frameon=False)
    save_fig("01_daily_traffic_analysis")


# 2.小时行为分布分析

def hour_traffic_analysis():
    df = read_table("ads_hour_traffic").copy()

    # 计算PV->购买转化率
    df['pv_to_buy_rate'] = df['buy_count'] / df['pv_count'].replace(0, np.nan)

    # 保存数据表
    save_csv(df, "ads_hour_traffic.csv")

    fig, ax = plt.subplots(2,1,figsize=(12, 10),sharex=True)
    fig.patch.set_facecolor('white')
    ax[0].set_facecolor('white')
    ax[1].set_facecolor('white')
    
    # 图2（a）24小时行为分布
    
    # 由于 PV 与 加购/购买/收藏数的量级不同，
    # 为避免共用同一 y 轴时曲线被压扁，这里采用左右双轴展示。
    # 左轴：加购/购买/收藏数量折线图
    line_cart = ax[0].plot(
        df['event_hour'], df['cart_count'],
        marker='o', linewidth=2, markersize=5, 
        label='加购'
    )
    line_buy = ax[0].plot(
        df['event_hour'], df['buy_count'],
        marker='o', linewidth=2, markersize=5, 
        label='购买'
    )
    line_fav = ax[0].plot(
        df['event_hour'], df['fav_count'],
        marker='o', linewidth=2, markersize=5, 
        label='收藏'
    )
    ax[0].set_title('图2（a）24小时行为分布', fontsize=14, pad=12)
    ax[0].set_ylabel('行为数量')
    ax[0].grid(True, linestyle='--', alpha=0.3)
    
    # 右轴：PV数量折线图
    ax1 = ax[0].twinx()
    line_pv = ax1.plot(
        df['event_hour'], df['pv_count'],
        marker='o', linewidth=2, markersize=5, color='r',
        label='PV'
    )
    ax1.set_ylabel('PV')
    
    # 合并图例
    lines = line_pv + line_cart + line_buy + line_fav
    labels = [l.get_label() for l in lines]
    ax[0].legend(lines, labels, loc='upper left', frameon=False)
    
    # 图2（b）24小时PV->购买转化率柱状图
    ax[1].bar(df['event_hour'], df['pv_to_buy_rate'])
    ax[1].set_title('图2（b）24小时PV->购买转化率柱状图', fontsize=14, pad=12)
    ax[1].set_ylabel('PV->购买转化率')
    ax[1].set_xlabel('小时')
    ax[1].grid(True, linestyle='--', alpha=0.3)
    # y轴以百分号形式显示
    ax[1].yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    save_fig("02_hour_traffic_analysis")


# 3.用户-商品行为路径分析

def user_item_flags():
    df = read_table("ads_user_item_flags").copy()
    
    # 保存数据表
    # save_csv(df, "ads_user_item_flags.csv")
    
    # 路径分类（行为组合）
    conditions = [
        (df['buy_count'] > 0) & (df['cart_count'] > 0),
        (df['buy_count'] > 0) & (df['fav_count'] > 0) & (df['cart_count'] == 0),
        (df['buy_count'] > 0) & (df['pv_count'] > 0) & (df['fav_count'] == 0) & (df['cart_count'] == 0),
        (df['buy_count'] == 0) & (df['cart_count'] > 0),
        (df['buy_count'] == 0) & (df['fav_count'] > 0) & (df['cart_count'] == 0),
        (df['buy_count'] == 0) & (df['pv_count'] > 0) & (df['fav_count'] == 0) & (df['cart_count'] == 0)
    ]
    choices = ['加购后购买',
               '收藏后购买',
               '浏览后直接购买', 
               '加购未购', 
               '收藏未购', 
               '仅浏览未转化'
              ]
    df['journey_type'] = np.select(conditions, choices, default='其他路径')
    
    # 路径汇总
    journey_summary = (
        df['journey_type']
        .value_counts()
        .rename_axis('journey_type')
        .reset_index(name='count')
    )
    journey_summary['share'] = journey_summary['count'] / journey_summary['count'].sum()

    # 可视化
    plot_df = journey_summary.sort_values('count', ascending=True)
    plot_df2 = plot_df[plot_df['journey_type'] != '仅浏览未转化']
    
    fig, ax = plt.subplots(1,2,figsize=(18, 6))
    fig.patch.set_facecolor('white')
    ax[0].set_facecolor('white')
    ax[1].set_facecolor('white')
    
    # 图3（a）用户-商品行为路径图    
    bars = ax[0].barh(plot_df['journey_type'], plot_df['share'])
    
    for i, (cnt, pct) in enumerate(zip(plot_df['count'], plot_df['share'])):
        ax[0].text(pct, i, f'  {cnt} ({pct*100:.2f}%)', va='center')
        
    ax[0].set_title('图3（a）用户-商品行为路径图', fontsize=14, pad=12)
    ax[0].grid(axis='x', linestyle='--', alpha=0.3)
    ax[0].set_xlabel('占比')
    # x轴以百分号形式显示
    ax[0].xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    
    # 图3（b）用户-商品行为路径补充图
    # 剔除“仅浏览未转化”后的路径分布
    bars2 = ax[1].barh(plot_df2['journey_type'], plot_df2['share'])
    
    for i, (cnt, pct) in enumerate(zip(plot_df2['count'], plot_df2['share'])):
        ax[1].text(pct, i, f'  {cnt} ({pct*100:.2f}%)', va='center')
        
    ax[1].set_title('图3（b）用户-商品（剔除“仅浏览未转化”后）行为路径图', fontsize=14, pad=12)
    ax[1].grid(axis='x', linestyle='--', alpha=0.3)
    ax[1].set_xlabel('占比')
    # x轴以百分号形式显示
    ax[1].xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    save_fig("03_user_item_journey")


# 4.用户画像分析

# 评分函数
def score_by_quantile(series, reverse=False):
    """
    将变量按五分位打分：
    reverse=False: 值越大分越高
    reverse=True : 值越小分越高
    """
    # 对series进行排名
    ranked = series.rank(method='first')

    if reverse:
        score = pd.qcut(ranked, 5, labels=[5, 4, 3, 2, 1])
    else:
        score = pd.qcut(ranked, 5, labels=[1, 2, 3, 4, 5])
    return score.astype(int)
    
def user_profile_analysis():
    df = read_table("ads_user_profile").copy()
    df['last_event_date'] = pd.to_datetime(df['last_event_date'])

    # 构造RF指标
    # 对照日：取全表最近日期
    date = df['last_event_date'].max()
    
    # R：距离最近一次活跃（对照日）过去多少天
    df['recency_days'] = (date - df['last_event_date']).dt.days

    # F：购买频次
    df['frequency'] = df['buy_count']

    # R 越小评分越高
    df['R_score'] = score_by_quantile(df['recency_days'], reverse=True)
    # F 越大评分越高
    df['F_score'] = score_by_quantile(df['frequency'], reverse=False)
    # 活跃天数作为辅助指标
    df['A_score'] = score_by_quantile(df['active_days'], reverse=False)

    # 用户分群
    
    conditions = [
    (df['R_score'] >= 4) & (df['F_score'] >= 4) & (df['A_score'] >= 4),
    (df['R_score'] >= 4) & (df['F_score'] >= 3) & (df['A_score'] >= 3),
    (df['R_score'] >= 4) & (df['A_score'] >= 4) & (df['F_score'] <= 2),
    (df['R_score'] <= 2) & ((df['F_score'] >= 4) | (df['A_score'] >= 4)),
    (df['R_score'] <= 2) & (df['F_score'] <= 2) & (df['A_score'] <= 2)
    ]
    choices = [
        '核心高价值用户',
        '重要发展用户',
        '高活跃低转化用户',
        '重要召回用户',
        '沉默用户'
    ]   
    df['user_segment'] = np.select(conditions, choices, default='一般发展用户')
    # 保存数据表
    save_csv(df, "ads_user_segment.csv")

    # 统计各类用户数量
    segment_counts = df['user_segment'].value_counts()
    total = segment_counts.sum()

    # 图4 各类用户占比分布
    plt.figure(figsize=(8, 8))
    
    labels = [
        f'{idx}\n{cnt}人 ({cnt/total:.1%})'
        for idx, cnt in zip(segment_counts.index, segment_counts.values)
    ]   
    plt.pie(
        segment_counts,
        labels=labels,
        startangle=90,
        counterclock=False,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1}
    )    
    plt.title('图4 各类用户占比分布')
    save_fig("04_user_segment_ratio")


# ===== 执行模块 =====

if __name__ == "__main__":
    daily_traffic_analysis()
    hour_traffic_analysis()
    user_item_flags()
    user_profile_analysis()
