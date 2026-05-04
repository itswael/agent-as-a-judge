from src.config_loader import MetricWeightConfig


def main():
    config = MetricWeightConfig("configs/metric_weights.yaml")
    weights = config.load()

    print("Loaded metric weights:")
    print(weights)


if __name__ == "__main__":
    main()