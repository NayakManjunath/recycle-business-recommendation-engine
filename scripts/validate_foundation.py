from pathlib import Path
import json
import importlib.util
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def check_path(path: Path, description: str) -> None:
    if not path.exists():
        raise AssertionError(f"Missing {description}: {path}")


def check_import(package: str) -> None:
    if importlib.util.find_spec(package) is None:
        raise AssertionError(f"Missing dependency: {package}")


def validate_data_contracts() -> None:
    contract_path = PROJECT_ROOT / "configs" / "data_contracts.json"

    with contract_path.open("r", encoding="utf-8") as file:
        contracts = json.load(file)

    expected_contracts = {
        "material_byproduct",
        "waste_stream",
        "recycling_process",
        "secondary_market_demand",
    }

    actual_contracts = set(contracts.keys())

    if actual_contracts != expected_contracts:
        raise AssertionError(
            f"Data contracts mismatch. "
            f"Expected: {expected_contracts}, "
            f"Found: {actual_contracts}"
        )

    for contract_name, contract in contracts.items():
        if "description" not in contract:
            raise AssertionError(
                f"Missing description in contract: {contract_name}"
            )

        if "required_fields" not in contract:
            raise AssertionError(
                f"Missing required_fields in contract: {contract_name}"
            )

        if not contract["required_fields"]:
            raise AssertionError(
                f"No required fields defined: {contract_name}"
            )


def main() -> None:
    print("=== Foundation Validation ===")

    # Python version
    print(f"[PASS] Python: {sys.version.split()[0]}")

    # Required project directories
    required_directories = [
        "data",
        "data/raw",
        "data/processed",
        "data/sample",
        "src",
        "src/data_pipeline",
        "src/matching",
        "src/compatibility",
        "src/carbon",
        "src/api",
        "src/streamlit_app",
        "tests",
        "notebooks",
        "configs",
        "scripts",
    ]

    for directory in required_directories:
        check_path(
            PROJECT_ROOT / directory,
            f"directory '{directory}'",
        )

    print("[PASS] Project directories")

    # Required files
    required_files = [
        ".gitignore",
        "README.md",
        "requirements.txt",
        "src/__init__.py",
        "src/data_pipeline/__init__.py",
        "src/matching/__init__.py",
        "src/compatibility/__init__.py",
        "src/carbon/__init__.py",
        "src/api/__init__.py",
        "configs/data_contracts.json",
    ]

    for file_name in required_files:
        check_path(
            PROJECT_ROOT / file_name,
            f"file '{file_name}'",
        )

    print("[PASS] Required project files")

    # Required dependencies
    dependencies = [
        "pandas",
        "sklearn",
        "fastapi",
        "streamlit",
        "uvicorn",
    ]

    for package in dependencies:
        check_import(package)

    print("[PASS] Required dependencies")

    # Data contracts
    validate_data_contracts()

    print("[PASS] Data contracts")

    print()
    print("FOUNDATION VALIDATION: PASSED")


if __name__ == "__main__":
    main()