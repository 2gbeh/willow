import json

from rp_handler import validate_input


def run_validation_tests():
    with open("test_input.json") as f:
        payload = json.load(f)

    validated, error = validate_input(payload["input"])
    assert error is None, f"Expected no error, got: {error}"
    assert validated["prompt"] == payload["input"]["prompt"]
    print("valid input passed:", validated)

    validated, error = validate_input({})
    assert validated is None
    assert error == "'prompt' is required and must be a non-empty string."
    print("missing prompt correctly rejected:", error)

    validated, error = validate_input({"prompt": "a cat", "width": -1})
    assert validated is None
    assert "width" in error
    print("bad width correctly rejected:", error)


if __name__ == "__main__":
    run_validation_tests()
    print("all tests passed")
