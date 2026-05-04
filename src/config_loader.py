import yaml


class MetricWeightConfig:
    def __init__(self, config_path: str):
        self.config_path = config_path

    def load(self):
        with open(self.config_path, "r") as file:
            weights = yaml.safe_load(file)

        total = sum(weights.values())

        if round(total, 2) != 1.00:
            raise ValueError(f"Metric weights must sum to 1.0, got {total}")

        return weights