-- 每日流量表
CREATE TABLE ads_daily_traffic AS
SELECT
    event_date,
    COUNT(*) AS total_behaviors,
    COUNT(DISTINCT user_id) AS uv,
    SUM(behavior_type = 'pv') AS pv_count,
    SUM(behavior_type = 'fav') AS fav_count,
    SUM(behavior_type = 'cart') AS cart_count,
    SUM(behavior_type = 'buy') AS buy_count
FROM user_behavior_clean
GROUP BY event_date
ORDER BY event_date;

-- 小时流量与行为汇总表
CREATE TABLE ads_hour_traffic AS
    SELECT
        event_hour,
        COUNT(*) AS total_behaviors,
        COUNT(DISTINCT user_id) AS uv,
        SUM(behavior_type = 'pv') AS pv_count,
        SUM(behavior_type = 'fav') AS fav_count,
        SUM(behavior_type = 'cart') AS cart_count,
        SUM(behavior_type = 'buy') AS buy_count
    FROM user_behavior_clean
    GROUP BY event_hour
    ORDER BY event_hour;

-- 用户-商品行为分布表
CREATE TABLE ads_user_item_flags AS
    SELECT
        user_id,
        item_id,
        SUM(behavior_type = 'pv') AS pv_count,
        SUM(behavior_type = 'fav') AS fav_count,
        SUM(behavior_type = 'cart') AS cart_count,
        SUM(behavior_type = 'buy') AS buy_count,
        COUNT(*) AS total_behaviors,
        MAX(event_date) AS last_event_date
    FROM user_behavior_clean
    GROUP BY user_id, item_id;

-- 用户画像表
CREATE TABLE ads_user_profile AS
    SELECT
        user_id,
        COUNT(*) AS total_behaviors,
        SUM(behavior_type = 'pv') AS pv_count,
        SUM(behavior_type = 'fav') AS fav_count,
        SUM(behavior_type = 'cart') AS cart_count,
        SUM(behavior_type = 'buy') AS buy_count,
        MAX(event_date) AS last_event_date,
        MIN(event_date) AS first_event_date,
        COUNT(DISTINCT event_date) AS active_days
    FROM user_behavior_clean
    GROUP BY user_id;


