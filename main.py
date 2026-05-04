from src.dataset_loader import DatasetLoader


def main():
    file_path = "data/sample.xlsx"

    loader = DatasetLoader(file_path)
    records = loader.load()

    print(f"Loaded {len(records)} records")

    if records:
        print("First record:")
        print(records[0])


if __name__ == "__main__":
    main()