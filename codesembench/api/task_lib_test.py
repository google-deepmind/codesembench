"""Tests for task_lib."""

import math
import pytest
import asyncio
from typing import List, Set

from etils import epath
import rich
import rich.progress

from codesembench.api import task_lib
from codesembench.api import task_loader
from codesembench.api import test_utils


def test_alias_prf1(tmpdir):
  tasks_path = test_utils.get_tasks_path()
  tasks = task_loader.load_tasks(tasks_path)
  assert len(tasks) > 0

  task = test_utils._get_task_by_name(tasks, "simple_c_alias")

  progress = rich.progress.Progress()
  logdir = epath.Path(tmpdir)
  results_dict = asyncio.run(task.run(test_utils.MockLlm(), logdir, progress))
  assert set(["precision", "recall", "f1"]) == set(results_dict.keys())
  assert math.isclose(results_dict["precision"], 0.733333, abs_tol=1e-3)
  assert math.isclose(results_dict["recall"], 0.611111, abs_tol=1e-3)
  assert math.isclose(results_dict["f1"], 0.638886, abs_tol=1e-3)


@pytest.mark.parametrize(
    "type_str, expected_type",
    [
      ("str", str),
      ("List", List),
      ("List[List[str]]", List[List[str]]),
      ("Set[str]", Set[str]),
    ]
)
def test_parse_type(type_str, expected_type):
  assert task_lib._parse_type(type_str) == expected_type
