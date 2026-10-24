# lesson5_file_handling.py
import json
from pathlib import Path


def load_sop_file(file_path: str) -> dict:
    """
    Safely loads an SOP JSON file from disk.
    Catches FileNotFoundError and JSON syntax errors gracefully.
    """
    path = Path(file_path)

    try:
        with open(path, "r", encoding="utf-8") as file:
            data: dict = json.load(file)
            return {
                "success": True,
                "data": data,
                "error": None
            }
    except FileNotFoundError:
        return {
            "success": False,
            "data": None,
            "error": f"File not found: '{file_path}'"
        }
    except json.JSONDecodeError as err:
        return {
            "success": False,
            "data": None,
            "error": f"Malformed JSON: {err.msg} at line {err.lineno}"
        }
    except Exception as err:
        return {
            "success": False,
            "data": None,
            "error": f"Unexpected error: {str(err)}"
        }


if __name__ == "__main__":
    print("=== Test 1: Loading valid SOP ===")
    result = load_sop_file("./data/sample_sop.json")
    if result["success"]:
        sop_data = result["data"]
        print(f"Loaded: {sop_data['sop_id']} - {sop_data['title']}")
        print(f"Rules: {list(sop_data['specifications'].keys())}")
    else:
        print(f"Error: {result['error']}")

    print("\n=== Test 2: Loading missing file ===")
    missing_result = load_sop_file("data/missing_file.json")
    print(f"Success: {missing_result['success']}")
    print(f"Handled Error: {missing_result['error']}")