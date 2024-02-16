"""Tests for evaluation_suite."""

import pytest
from etils import epath
from codesembench.api import evaluation_suite
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


def test_evaluation_suite_returns_correct_output(tmpdir):
  output_dir = epath.Path(tmpdir)
  suite = evaluation_suite.load_evaluation_suite(
      test_utils.get_tasks_path(),
      test_utils.MockLlm(),
      output_dir,
  )
  suite.run_suite(None)
  output_text = (output_dir / "eval_summary.md").read_text()
  assert output_text == _EXPECTED_OUTPUT
