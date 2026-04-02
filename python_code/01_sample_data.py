# 从源数据集中抽取前500万行数据作为子样本数据集
import pandas as pd

input_file = r"D:/xxx/UserBehavior.csv"
output_file = "UserBehavior_500w.csv"

n_rows = 5000000

df = pd.read_csv(input_file, header=None, nrows=n_rows)
df.to_csv(output_file, index=False, header=False, encoding="utf-8-sig")

print("已保存前500w行数据到", output_file)
print(df.head())