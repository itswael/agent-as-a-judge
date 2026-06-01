import json
import pandas as pd


class DatasetLoader:

    REQUIRED_COLUMNS = [
        "QUESTIONS",
        "ANSWERS GIVEN BY CHATBOT WITH MINIMUM CONTEXT",
        "ANSWERS GIVEN BY AGRICULTURAL CHATBOT",
    ]

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self):

        df = pd.read_excel(self.file_path)

        missing_columns = [
            col
            for col in self.REQUIRED_COLUMNS
            if col not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        df = df.dropna(
            subset=self.REQUIRED_COLUMNS
        )

        records = []

        for index, row in df.iterrows():
            records.append(
                {
                    "id": int(index),
                    "question": str(row["QUESTIONS"]).strip(),
                    "minimum_context_answer": str(row["ANSWERS GIVEN BY CHATBOT WITH MINIMUM CONTEXT"]).strip(),
                    "agricultural_chatbot_answer": str(row["ANSWERS GIVEN BY AGRICULTURAL CHATBOT"]).strip(),
                }
            )

        return records