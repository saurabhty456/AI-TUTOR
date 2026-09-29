SQL_QUESTION_BANK = [
    {
        "prompt": (
            "For every product category, return the top two products by revenue "
            "from completed orders. Revenue is quantity multiplied by unit_price. "
            "Include ties at the second rank. Return category, product_name, "
            "revenue_rank, and revenue, ordered by category and rank."
        ),
        "tables": [
            {
                "name": "products",
                "columns": [
                    ["product_id", "INTEGER"],
                    ["product_name", "TEXT"],
                    ["category", "TEXT"],
                ],
                "visible": [
                    [1, "Keyboard", "Peripherals"],
                    [2, "Mouse", "Peripherals"],
                    [3, "Webcam", "Peripherals"],
                    [4, "Chair", "Furniture"],
                    [5, "Desk", "Furniture"],
                ],
                "hidden": [
                    [1, "Keyboard", "Peripherals"],
                    [2, "Mouse", "Peripherals"],
                    [3, "Webcam", "Peripherals"],
                    [4, "Chair", "Furniture"],
                    [5, "Desk", "Furniture"],
                ],
            },
            {
                "name": "orders",
                "columns": [["order_id", "INTEGER"], ["status", "TEXT"]],
                "visible": [
                    [101, "completed"], [102, "completed"], [103, "completed"],
                    [104, "completed"], [105, "completed"], [106, "completed"],
                    [107, "cancelled"],
                ],
                "hidden": [
                    [101, "completed"], [102, "completed"], [103, "completed"],
                    [104, "completed"], [105, "completed"], [106, "completed"],
                    [107, "cancelled"], [108, "completed"],
                ],
            },
            {
                "name": "order_items",
                "columns": [
                    ["order_id", "INTEGER"],
                    ["product_id", "INTEGER"],
                    ["quantity", "INTEGER"],
                    ["unit_price", "NUMERIC"],
                ],
                "visible": [
                    [101, 1, 2, 100], [101, 2, 3, 40], [102, 1, 1, 100],
                    [103, 3, 2, 80], [104, 2, 2, 40], [105, 4, 1, 250],
                    [106, 5, 1, 300], [107, 1, 99, 100],
                ],
                "hidden": [
                    [101, 1, 2, 100], [101, 2, 3, 40], [102, 1, 1, 100],
                    [103, 3, 2, 80], [104, 2, 2, 40], [105, 4, 1, 250],
                    [106, 5, 1, 300], [107, 1, 99, 100], [108, 3, 1, 40],
                ],
            },
        ],
        "expected_visible": [
            {"category": "Furniture", "product_name": "Desk", "revenue_rank": 1, "revenue": 300},
            {"category": "Furniture", "product_name": "Chair", "revenue_rank": 2, "revenue": 250},
            {"category": "Peripherals", "product_name": "Keyboard", "revenue_rank": 1, "revenue": 300},
            {"category": "Peripherals", "product_name": "Mouse", "revenue_rank": 2, "revenue": 200},
        ],
        "expected_hidden": [
            {"category": "Furniture", "product_name": "Desk", "revenue_rank": 1, "revenue": 300},
            {"category": "Furniture", "product_name": "Chair", "revenue_rank": 2, "revenue": 250},
            {"category": "Peripherals", "product_name": "Keyboard", "revenue_rank": 1, "revenue": 300},
            {"category": "Peripherals", "product_name": "Mouse", "revenue_rank": 2, "revenue": 200},
            {"category": "Peripherals", "product_name": "Webcam", "revenue_rank": 2, "revenue": 200},
        ],
    },
    {
        "prompt": (
            "Using the customers and orders tables, calculate each customer's "
            "completed-order revenue by calendar month, then return each monthly "
            "total and the customer's running revenue through that month. Include "
            "only rows where cumulative revenue is at least 500. Return customer_name, "
            "month_start, monthly_revenue, and running_revenue ordered by customer "
            "and month. A customer with no qualifying rows should be omitted."
        ),
        "tables": [
            {
                "name": "customers",
                "columns": [["customer_id", "INTEGER"], ["customer_name", "TEXT"]],
                "visible": [[1, "Cora"], [2, "Dev"]],
                "hidden": [[1, "Cora"], [2, "Dev"], [3, "Eli"]],
            },
            {
                "name": "orders",
                "columns": [
                    ["order_id", "INTEGER"],
                    ["customer_id", "INTEGER"],
                    ["ordered_at", "DATE"],
                    ["status", "TEXT"],
                    ["amount", "NUMERIC"],
                ],
                "visible": [
                    [201, 1, "2025-01-08", "completed", 300],
                    [202, 1, "2025-02-11", "completed", 250],
                    [203, 2, "2025-01-15", "completed", 600],
                    [204, 2, "2025-02-03", "cancelled", 900],
                ],
                "hidden": [
                    [201, 1, "2025-01-08", "completed", 300],
                    [202, 1, "2025-02-11", "completed", 250],
                    [203, 2, "2025-01-15", "completed", 600],
                    [204, 2, "2025-02-03", "cancelled", 900],
                    [205, 1, "2025-01-29", "completed", 100],
                    [206, 3, "2025-02-09", "completed", 700],
                ],
            },
        ],
        "expected_visible": [
            {"customer_name": "Cora", "month_start": "2025-02-01", "monthly_revenue": 250, "running_revenue": 550},
            {"customer_name": "Dev", "month_start": "2025-01-01", "monthly_revenue": 600, "running_revenue": 600},
        ],
        "expected_hidden": [
            {"customer_name": "Cora", "month_start": "2025-02-01", "monthly_revenue": 250, "running_revenue": 650},
            {"customer_name": "Dev", "month_start": "2025-01-01", "monthly_revenue": 600, "running_revenue": 600},
            {"customer_name": "Eli", "month_start": "2025-02-01", "monthly_revenue": 700, "running_revenue": 700},
        ],
    },
]

SYSTEM_DESIGN_QUESTIONS = [
    "Design a multi-region URL shortener that handles 50,000 writes per second and 500,000 reads per second. Cover API design, key generation, storage, caching, analytics, abuse prevention, and behavior during a regional outage.",
    "Design a collaborative document editor for 2 million daily users. Explain real-time synchronization, conflict resolution, persistence, sharing permissions, offline edits, and how you would keep latency low across regions.",
    "Design a ride dispatch service for a large city. Cover driver location ingestion, nearby-driver matching, trip state, peak-load scaling, location freshness, and failure handling when mapping or notification services are unavailable.",
]
