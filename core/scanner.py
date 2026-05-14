import os
import importlib
from core.rule_loader import load_rules
from core.context_tracker import get_tainted_variables


def scan_tree(tree, file_path):

    if tree is None:
        return []

    issues = []

    # Get tainted variables
    tainted_variables = get_tainted_variables(tree)

    # Load rule metadata
    rules_metadata = load_rules()

    base_path = os.path.dirname(os.path.dirname(__file__))
    rules_path = os.path.join(base_path, "rules")

    for filename in os.listdir(rules_path):

        if filename.endswith(".py") and filename != "__init__.py":

            module_name = filename[:-3]

            try:
                module = importlib.import_module(f"rules.{module_name}")

                rule_id = None
                for key, value in rules_metadata.items():
                    if value["name"].lower().replace(" ", "_") == module_name:
                        rule_id = key
                        break

                if rule_id is None:
                    continue

                if hasattr(module, "detect"):
                    issues.extend(
                        module.detect(
                            tree,
                            file_path,
                            rules_metadata[rule_id],
                            tainted_variables  # 🔥 NEW PARAMETER
                        )
                    )

            except Exception as e:
                print(f"Error loading rule {module_name}: {e}")

    return issues