"""Tests for task_lib."""

import pytest
import asyncio
from typing import List, Set

from etils import epath
import rich
import rich.progress

from codesembench.api import task_lib
from codesembench.api import task_loader
from codesembench.api import test_utils
from google3.testing.pybase import parameterized


def test_alias_prf1(self):
  tasks_path = test_utils.get_tasks_path()
  tasks = task_loader.load_tasks(tasks_path)
  self.assertNotEmpty(tasks)

  task = test_utils._get_task_by_name(tasks, "simple_c_alias")

  progress = rich.progress.Progress()
  logdir = epath.Path(self.create_tempdir())
  results_dict = asyncio.run(task.run(test_utils.MockLlm(), logdir, progress))
  self.assertSameElements(["precision", "recall", "f1"], results_dict.keys())
  self.assertAlmostEqual(results_dict["precision"], 0.733333, places=5)
  self.assertAlmostEqual(results_dict["recall"], 0.611111, places=5)
  self.assertAlmostEqual(results_dict["f1"], 0.638886, places=5)

@pytest.mark.parametrize(
    "type_str", "expected_type"
    [
      ("str", str),
      ("List", List),
      ("List[List[str]]", List[List[str]]),
      ("Set[str]", Set[str]),
    ]
)
def test_parse_type(self, type_str, expected_type):
  self.assertEqual(task_lib._parse_type(type_str), expected_type)
