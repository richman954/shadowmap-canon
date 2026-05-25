import json
import unittest
from pathlib import Path
from jsonschema import validate, ValidationError

class TestSchemas(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.schemas_dir = self.repo_root / "schemas"
        self.examples_dir = self.repo_root / "examples" / "schema_records"

    def test_analysis_schema_valid(self):
        schema_path = self.schemas_dir / "shadowmap_analysis.schema.json"
        example_path = self.examples_dir / "example_analysis.json"

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        with open(example_path, "r", encoding="utf-8") as f:
            example = json.load(f)

        validate(instance=example, schema=schema)

    def test_analysis_schema_invalid_enum(self):
        schema_path = self.schemas_dir / "shadowmap_analysis.schema.json"
        example_path = self.examples_dir / "example_analysis.json"

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        with open(example_path, "r", encoding="utf-8") as f:
            example = json.load(f)

        example["verdict"] = "invalid verdict"
        with self.assertRaises(ValidationError):
            validate(instance=example, schema=schema)

        example["verdict"] = "strong ShadowMap"
        example["confidence"] = "invalid confidence"
        with self.assertRaises(ValidationError):
            validate(instance=example, schema=schema)

    def test_transfer_schema_valid(self):
        schema_path = self.schemas_dir / "transfer_result.schema.json"
        example_path = self.examples_dir / "example_transfer.json"

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        with open(example_path, "r", encoding="utf-8") as f:
            example = json.load(f)

        validate(instance=example, schema=schema)

    def test_transfer_schema_invalid_bounds(self):
        schema_path = self.schemas_dir / "transfer_result.schema.json"
        example_path = self.examples_dir / "example_transfer.json"

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        with open(example_path, "r", encoding="utf-8") as f:
            example = json.load(f)

        # Test zero or negative count
        example["node_count"] = 0
        with self.assertRaises(ValidationError):
            validate(instance=example, schema=schema)
        example["node_count"] = -1
        with self.assertRaises(ValidationError):
            validate(instance=example, schema=schema)
        example["node_count"] = 7

        example["factor_count"] = 0
        with self.assertRaises(ValidationError):
            validate(instance=example, schema=schema)

        example["factor_count"] = -1
        with self.assertRaises(ValidationError):
            validate(instance=example, schema=schema)

        example["factor_count"] = 9

        # Test probability > 1
        example["exact_high_probabilities"]["q_memory_high"] = 1.5
        with self.assertRaises(ValidationError):
            validate(instance=example, schema=schema)
        example["exact_high_probabilities"]["q_memory_high"] = 0.5

        # Test empty residuals
        example["top_factor_residuals"] = []
        with self.assertRaises(ValidationError):
            validate(instance=example, schema=schema)

    def test_constrained_search_schema_valid(self):
        schema_path = self.schemas_dir / "constrained_search.schema.json"
        example_path = self.examples_dir / "example_constrained_search.json"

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        with open(example_path, "r", encoding="utf-8") as f:
            example = json.load(f)

        validate(instance=example, schema=schema)

    def test_constrained_search_schema_invalid(self):
        schema_path = self.schemas_dir / "constrained_search.schema.json"
        example_path = self.examples_dir / "example_constrained_search.json"

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        with open(example_path, "r", encoding="utf-8") as f:
            example = json.load(f)

        example["iteration_limit"] = 0
        with self.assertRaises(ValidationError):
            validate(instance=example, schema=schema)

    def test_formal_proof_schema_valid(self):
        schema_path = self.schemas_dir / "formal_proof_result.schema.json"
        example_path = self.examples_dir / "example_formal_proof.json"

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        with open(example_path, "r", encoding="utf-8") as f:
            example = json.load(f)

        validate(instance=example, schema=schema)

    def test_formal_proof_schema_invalid(self):
        schema_path = self.schemas_dir / "formal_proof_result.schema.json"
        example_path = self.examples_dir / "example_formal_proof.json"

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        with open(example_path, "r", encoding="utf-8") as f:
            example = json.load(f)

        example["is_valid"] = "maybe"
        with self.assertRaises(ValidationError):
            validate(instance=example, schema=schema)

if __name__ == "__main__":
    unittest.main()
