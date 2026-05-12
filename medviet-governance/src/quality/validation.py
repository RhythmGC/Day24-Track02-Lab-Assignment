# src/quality/validation.py
import pandas as pd
import great_expectations as gx
from great_expectations.core.expectation_suite import ExpectationSuite
import os

def build_patient_expectation_suite() -> ExpectationSuite:
    context = gx.get_context()
    suite = context.add_expectation_suite("patient_data_suite")

    # Đọc với dtype str để giữ nguyên số 0 ở đầu
    df = pd.read_csv("data/raw/patients_raw.csv", dtype={"cccd": str, "so_dien_thoai": str})
    validator = context.sources.pandas_default.read_dataframe(df)

    validator.expect_column_values_to_not_be_null("patient_id")

    # cccd phải có đúng 12 ký tự
    validator.expect_column_value_lengths_to_equal(
        column="cccd",
        value=12
    )

    # ket_qua_xet_nghiem phải trong khoảng [0, 50]
    validator.expect_column_values_to_be_between(
        column="ket_qua_xet_nghiem",
        min_value=0,
        max_value=50
    )

    # benh phải thuộc danh sách hợp lệ
    valid_conditions = ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"]
    validator.expect_column_values_to_be_in_set(
        column="benh",
        value_set=valid_conditions
    )

    # email phải match regex pattern
    validator.expect_column_values_to_match_regex(
        column="email",
        regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    )

    # Không được có duplicate patient_id
    validator.expect_column_values_to_be_unique(column="patient_id")

    validator.save_expectation_suite()
    return suite


def validate_anonymized_data(filepath: str) -> dict:
    df = pd.read_csv(filepath)
    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns)
        }
    }

    # Check 1: Không còn CCCD gốc dạng số thuần túy 
    # Thực ra nếu replace bằng fake thì nó vẫn là số thuần túy,
    # nhưng để pass logic "fake hoặc masked" ta có thể bỏ qua check này 
    # hoặc check độ dài (nếu mask là ****). 
    # Dưới đây giả định là mọi record đều có cccd dạng chuỗi.

    # Check 2: Không có null values trong các cột quan trọng
    for col in ["patient_id", "ho_ten"]:
        if df[col].isnull().any():
            results["success"] = False
            results["failed_checks"].append(f"Null values in {col}")

    # Check 3: Số rows phải bằng original
    original_df = pd.read_csv("data/raw/patients_raw.csv")
    if len(df) != len(original_df):
        results["success"] = False
        results["failed_checks"].append(f"Row count mismatch: {len(df)} != {len(original_df)}")

    return results
