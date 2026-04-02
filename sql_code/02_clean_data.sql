-- 各字段空值检查
SELECT
    -- 计算各个字段中空值的个数
    SUM(CASE WHEN user_id IS NULL THEN 1 ELSE 0 END) AS null_user_id,
    SUM(CASE WHEN item_id IS NULL THEN 1 ELSE 0 END) AS null_item_id,
    SUM(CASE WHEN category_id IS NULL THEN 1 ELSE 0 END) AS null_category_id,
    SUM(CASE WHEN behavior_type IS NULL THEN 1 ELSE 0 END) AS null_behavior_type,
    SUM(CASE WHEN ts IS NULL THEN 1 ELSE 0 END) AS null_ts
FROM user_behavior_raw;
-- 检查结果各字段无空值

-- 生成清洗后的明细表（user_behavior_clean）
CREATE TABLE user_behavior_clean AS
    SELECT DISTINCT
        user_id,
        item_id,
        category_id,
        behavior_type,
        -- 将Unix时间戳转成真正时间并提取日期字段和小时字段
        DATE (FROM_UNIXTIME(ts)) AS event_date,
        HOUR (FROM_UNIXTIME(ts)) AS event_hour
FROM user_behavior_raw
-- 由于已对数据进行空值检查并认定无空值，故省略过滤空值的步骤
-- 过滤非法行为值
WHERE behavior_type IN ('pv','buy','cart','fav')
-- 过滤异常日期（2017年11月25日至2017年12月3日之外的日期）
AND DATE (FROM_UNIXTIME(ts)) BETWEEN '2017-11-25' AND '2017-12-3';


SELECT COUNT(*) FROM user_behavior_clean;
-- 共4579067行数据





