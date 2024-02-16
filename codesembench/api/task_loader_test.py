"""Tests for task_loader.py."""

import pytest
import typing
from codesembench.api import task_lib
from codesembench.api import task_loader
from codesembench.api import test_utils

def test_loading_simple_tasks():
  tasks_path = test_utils.get_tasks_path()
  tasks = task_loader.load_tasks(tasks_path)

  assert len(tasks) == 2

  task_names = [task.name for task in tasks]
  assert set(task_names) == set(["simple_c_alias", "simple_c_escape"])

  for task in tasks:
    assert task.language == task_lib.Language.C

  alias_task = test_utils._get_task_by_name(tasks, "simple_c_alias")
  alias_task = typing.cast(task_lib.PropertyPredictionTask, alias_task)
  for program in alias_task.data:
    assert isinstance(program.gold_answer, list)
