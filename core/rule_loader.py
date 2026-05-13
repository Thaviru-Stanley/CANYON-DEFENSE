import json
import os


def load_rules():
    base_path = os.path.dirname(os.path.dirname(__file__))
    rules_path = os.path.join(base_path, "rules", "rules.json")

    with open(rules_path, "r", encoding="utf-8") as f:
        return json.load(f)