INSERT_PRODUCT_COST = """
INSERT INTO product_name(user_id, product_name, category_id, price, created_at)
VALUES ({user_id}, '{product_name}', {category_id}, {cost}, '{created_at}')"""

INSERT_CATEGORY_COST = """
INSERT INTO cost_category(user_id, cost_sum, category_id, month)
VALUES ({user_id}, '{cost_sum}', {category_id}, {month})
"""

GET_ALL_COST_PRODUCT = """SELECT SUM(price) as all_cost FROM product_name pn
GROUP BY user_id
HAVING user_id={user_id}"""


GET_COST_PER_CATEGORY_FOR_NOW_MONTH = """
SELECT SUM(cost_sum) AS cost, category_id  AS category FROM cost_category c
WHERE user_id=383333437 AND month = CAST(strftime('%m', 'now') AS INTEGER)
GROUP BY category_id;
"""
