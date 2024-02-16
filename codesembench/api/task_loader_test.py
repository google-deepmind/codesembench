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
