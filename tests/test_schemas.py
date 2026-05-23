import json
import unittest
from pathlib import Path
from jsonschema import validate

class TestSchemas(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.schemas_dir = self.repo_root / "schemas"
        self.examples_dir = self.repo_root / "examples" / "schema_records"

    def test_analysis_schema(self):
        schema_path = self.schemas_dir / "shadowmap_analysis.schema.json"
        example_path = self.examples_dir / "example_analysis.json"

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        with open(example_path, "r", encoding="utf-8") as f:
            example = json.load(f)

        validate(instance=example, schema=schema)

    def test_transfer_schema(self):
        schema_path = self.schemas_dir / "transfer_result.schema.json"
        example_path = self.examples_dir / "example_transfer.json"

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        with open(example_path, "r", encoding="utf-8") as f:
            example = json.load(f)

        validate(instance=example, schema=schema)

if __name__ == "__main__":
    unittest.main()
