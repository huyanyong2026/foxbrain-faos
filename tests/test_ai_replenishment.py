import csv
import io
import unittest
from zipfile import ZipFile

from apps.ai.replenishment import (
    RULE_VERSION, build_excel, calculate_replenishment, normalize_input_rows, parse_uploaded_file,
)


def item(**overrides):
    base = {
        "store_code": "nanshan", "store_name": "南山店", "sku_code": "SKU-1",
        "product_name": "测试背包", "brand_name": "VAFOX", "category_name": "背包",
        "color": "黑", "size": "M", "available_stock": 2, "sales_30d": 15,
        "sales_prev_30d": 8,
    }
    base.update(overrides)
    return base


class ReplenishmentRuleTests(unittest.TestCase):
    def test_low_stock_calculates_integer_quantity_and_explanation(self):
        result = calculate_replenishment(item())
        self.assertEqual(result.recommendation, "replenish")
        self.assertEqual(result.priority, "紧急")
        self.assertEqual(result.suggested_qty, 13)
        self.assertIn("近30天销售15件", result.reason)
        self.assertIn("建议补货13件", result.reason)

    def test_exactly_fifteen_days_does_not_enter_trigger_list(self):
        result = calculate_replenishment(item(available_stock=15, sales_30d=30, sales_prev_30d=30))
        self.assertEqual(result.stock_days, 15)
        self.assertNotEqual(result.recommendation, "replenish")

    def test_growth_raises_high_priority_to_urgent(self):
        result = calculate_replenishment(item(available_stock=10, sales_30d=30, sales_prev_30d=10))
        self.assertEqual(result.stock_days, 10)
        self.assertEqual(result.priority, "紧急")
        self.assertIn("销量高于前30天", result.reason)

    def test_no_sales_for_sixty_days_never_replenishes(self):
        result = calculate_replenishment(item(available_stock=0, sales_30d=0, sales_prev_30d=0))
        self.assertEqual(result.priority, "不补")
        self.assertEqual(result.suggested_qty, 0)
        self.assertIsNone(result.stock_days)

    def test_negative_source_values_are_flagged_and_never_create_negative_qty(self):
        result = calculate_replenishment(item(available_stock=-3, sales_30d=-2, sales_prev_30d=5))
        self.assertGreaterEqual(result.suggested_qty, 0)
        self.assertEqual(result.sales_30d, 0)
        self.assertIn("负库存", result.warning)
        self.assertIn("负净销量", result.warning)

    def test_chinese_csv_is_normalized_for_three_stores(self):
        text = "门店,商品编码,商品名称,当前库存,近30天销售,前30天销售\n南山店,A1,背包,2,15,8\n航苑店,A2,鞋,5,10,4\n振兴店,A3,衣服,8,2,1\n"
        rows = parse_uploaded_file("sap.csv", text.encode("utf-8"))
        self.assertEqual({row["store_code"] for row in rows}, {"nanshan", "hangyuan", "zhenxing"})

    def test_duplicate_store_sku_is_rejected(self):
        rows = [
            {"门店": "南山店", "商品编码": "A1", "商品名称": "背包", "当前库存": 2, "近30天销售": 5, "前30天销售": 2},
            {"门店": "南山店", "商品编码": "A1", "商品名称": "背包", "当前库存": 2, "近30天销售": 5, "前30天销售": 2},
        ]
        with self.assertRaisesRegex(ValueError, "重复"):
            normalize_input_rows(rows)

    def test_missing_sixty_day_window_is_rejected(self):
        rows = [{"门店": "南山店", "商品编码": "A1", "商品名称": "背包", "当前库存": 2, "近30天销售": 5}]
        with self.assertRaisesRegex(ValueError, "前30天销售或近60天销售"):
            normalize_input_rows(rows)

    def test_excel_has_result_and_metadata_sheets(self):
        result = calculate_replenishment(item()).__dict__
        stream = build_excel([result], {"规则版本": RULE_VERSION, "数据来源": "test"})
        with ZipFile(stream) as archive:
            workbook = archive.read("xl/workbook.xml").decode("utf-8")
            self.assertIn("补货建议", workbook)
            self.assertIn("生成说明", workbook)


if __name__ == "__main__":
    unittest.main()
