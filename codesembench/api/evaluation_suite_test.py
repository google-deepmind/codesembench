#!/usr/bin/python
#
# Copyright 2024 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
