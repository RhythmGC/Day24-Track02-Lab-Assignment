# src/pii/anonymizer.py
import pandas as pd
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from faker import Faker
import random
from .detector import build_vietnamese_analyzer, detect_pii

fake = Faker("vi_VN")

class MedVietAnonymizer:

    def __init__(self):
        self.analyzer = build_vietnamese_analyzer()
        self.anonymizer = AnonymizerEngine()

    def anonymize_text(self, text: str, strategy: str = "replace") -> str:
        results = detect_pii(str(text), self.analyzer)
        if not results:
            return text

        operators = {}

        if strategy == "replace":
            operators = {
                "PERSON": OperatorConfig("replace", 
                          {"new_value": fake.name()}),
                "EMAIL_ADDRESS": OperatorConfig("replace", 
                                 {"new_value": fake.email()}),
                "VN_CCCD": OperatorConfig("replace", 
                           {"new_value": "".join([str(random.randint(0,9)) for _ in range(12)])}),
                "VN_PHONE": OperatorConfig("replace", 
                            {"new_value": f"09{''.join([str(random.randint(0,9)) for _ in range(8)])}"}),
            }
        elif strategy == "mask":
            mask_config = OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 4, "from_end": True})
            operators = {
                "PERSON": mask_config,
                "EMAIL_ADDRESS": mask_config,
                "VN_CCCD": mask_config,
                "VN_PHONE": mask_config
            }
        elif strategy == "hash":
            hash_config = OperatorConfig("hash", {"hash_type": "sha256"})
            operators = {
                "PERSON": hash_config,
                "EMAIL_ADDRESS": hash_config,
                "VN_CCCD": hash_config,
                "VN_PHONE": hash_config
            }

        anonymized = self.anonymizer.anonymize(
            text=str(text),
            analyzer_results=results,
            operators=operators
        )
        return anonymized.text

    def anonymize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df_anon = df.copy()

        # Text columns
        for col in ["ho_ten", "dia_chi", "email"]:
            if col in df_anon.columns:
                df_anon[col] = df_anon[col].apply(lambda x: self.anonymize_text(str(x)))
                
        # Direct replacement columns
        if "cccd" in df_anon.columns:
            df_anon["cccd"] = df_anon["cccd"].apply(lambda _: "".join([str(random.randint(0,9)) for _ in range(12)]))
        if "so_dien_thoai" in df_anon.columns:
            df_anon["so_dien_thoai"] = df_anon["so_dien_thoai"].apply(lambda _: f"09{''.join([str(random.randint(0,9)) for _ in range(8)])}")

        return df_anon

    def calculate_detection_rate(self, 
                                  original_df: pd.DataFrame,
                                  pii_columns: list) -> float:
        total = 0
        detected = 0

        for col in pii_columns:
            for value in original_df[col].astype(str):
                total += 1
                results = detect_pii(value, self.analyzer)
                if len(results) > 0:
                    detected += 1

        return detected / total if total > 0 else 0.0
