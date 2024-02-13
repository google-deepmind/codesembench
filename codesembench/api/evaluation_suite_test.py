"""Tests for evaluation_suite."""

import pytest
from etils import epath
from codesembench.api import evaluation_suite
from codesembench.api import task_lib
from codesembench.api import task_loader
from codesembench.api import test_utils

_EXPECTED_OUTPUT = """
## simple_c_alias

* precision: 0.733
* recall: 0.611
* f1: 0.639

## simple_c_escape

* precision: 0.000
* recall: 0.000
* f1: 0.000
"""


def test_evaluation_suite_returns_correct_output(self):
  output_dir = epath.Path(self.create_tempdir())
  suite = task_loader.load_evaluation_suite(
      test_utils.get_tasks_path(),
      test_utils.MockLlm(),
      output_dir,
  )
  suite.run_suite(None)
  output_text = (output_dir / "eval_summary.md").read_text()
  self.assertEqual(output_text, _EXPECTED_OUTPUT)
