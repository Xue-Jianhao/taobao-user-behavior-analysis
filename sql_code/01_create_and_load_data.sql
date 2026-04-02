-- 创建库
CREATE DATABASE  taobao_analysis ;
USE taobao_analysis;

-- 创建原始数据表（user_behavior_raw）
CREATE TABLE user_behavior_raw(
    user_id INT COMMENT '用户ID',
    item_id INT COMMENT '商品ID',
    category_id INT COMMENT '商品类目ID',
    behavior_type VARCHAR(5) COMMENT '行为类型',
    ts INT COMMENT '时间戳'
);

-- 导入子样本数据集
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/UserBehavior_500w.csv'
INTO TABLE user_behavior_raw
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
(user_id, item_id, category_id, behavior_type, ts);

