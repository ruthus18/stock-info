# Logic of algorithm:
#
# 1. Prepare stock prices enumared by date
# 2. Make cartesian join of stocks and build price difference graph
# 3. Find ascending paths with difference >= N
# 4. Group paths by their numbers and crop longer paths

PERIOD_ANALYTICS_SQL = """
    CREATE OR REPLACE LOCAL TEMP VIEW counted_stocks AS
    SELECT
        row_number() OVER (ORDER BY created_date) AS num,
        id, created_date, {type}_price as price
    FROM stocks_stockday
    WHERE company_id={company_id};

    CREATE OR REPLACE LOCAL TEMP VIEW filtered_graph AS
    SELECT * FROM
    (
        SELECT
            p1.id AS id1, p1.num AS num1, p1.created_date AS date1,
            p1.price AS price1,
            p2.id AS id2, p2.num AS num2, p2.created_date AS date2,
            p2.price AS price2,
            (p2.price - p1.price) AS diff
        FROM counted_stocks AS p1
        CROSS JOIN counted_stocks AS p2
        WHERE
            p1.num < p2.num
    ) AS diff_stocks_raw
    WHERE
        diff >= {min_diff} OR diff <= -{min_diff};

    SELECT id1, price1, date1, id2, price2, date2, diff
    FROM (
        SELECT *,
            max(num1) OVER (PARTITION BY num2) as max_num1,
            min(num2) OVER (PARTITION BY num1) as min_num2
        FROM filtered_graph
    ) AS clean_graph WHERE num1=max_num1 AND num2=min_num2;
"""
