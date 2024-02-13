"""Tests for task_loader.py."""

import pytest
import typing
from codesembench.api import task_lib
from codesembench.api import task_loader
from codesembench.api import test_utils

def test_loading_simple_tasks(self):
  tasks_path = test_utils.get_tasks_path()
  tasks = task_loader.load_tasks(tasks_path)

  self.assertLen(tasks, 2)

  task_names = [task.name for task in tasks]
  self.assertSameElements(task_names, ["simple_c_alias", "simple_c_escape"])

  for task in tasks:
    self.assertEqual(task.language, task_lib.Language.C)

  alias_task = test_utils._get_task_by_name(tasks, "simple_c_alias")
  alias_task = typing.cast(task_lib.PropertyPredictionTask, alias_task)
  for program in alias_task.data:
    self.assertIsInstance(program.gold_answer, list)
