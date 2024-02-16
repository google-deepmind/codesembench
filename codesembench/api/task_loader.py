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

"""Reads all the tasks that are identifiable from a given path.

Any directory that is a subdirectory of a given path and contains
a file called `metadata.json` will be interpreted as containing a task.
"""

import json
from typing import Any

from etils import epath

from codesembench.api import task_lib

METADATA_FILENAME = 'metadata.json'


def load_tasks(base_path: epath.Path) -> list[task_lib.Task]:
  """Loads all tasks in the given base path."""
  tasks = []
  for metadata_path in sorted(base_path.glob(f'*/{METADATA_FILENAME}')):
    tasks.append(load_one_task(metadata_path.parent))
  return tasks


def load_one_task(path: epath.Path) -> task_lib.Task:
  with open(path / METADATA_FILENAME, 'r') as f:
    task_metadata = json.load(f)
    task_obj = task_lib.PropertyPredictionTask.from_metadata(task_metadata)
    if task_obj.task_type == task_lib.TaskType.PER_FILE:
      task_obj.data = load_single_file_programs(task_obj, path)
    else:
      raise ValueError(f'Unknown task type: {task_obj.task_type}')
    return task_obj


def read_answer_text(path: epath.Path) -> Any:
  # Use epath read function rather than python open.
  answer_text = path.read_text(encoding='utf-8')
  return json.loads(answer_text)


def load_single_file_programs(
    task: task_lib.PropertyPredictionTask, path: epath.Path
):
  """Loads the programs and answers for a per-file task."""
  result = []
  for source_path in path.glob(task.file_pattern):
    try:
      program = source_path.read_text(encoding='utf-8')
      answer_path = path / task.answer_path / source_path.name
      answer = read_answer_text(answer_path)
      result.append(
          task_lib.SingleFileProgram(
              source_code=program,
              language=task.language,
              gold_answer=answer,
              output_type=task.output_type,
          )
      )
    except Exception as e:
      e.add_note(f'Could not read file: {source_path}')
      raise e
  return result
