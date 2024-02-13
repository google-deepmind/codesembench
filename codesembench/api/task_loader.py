"""Reads all the tasks that are identifiable from a given path.

Any directory that is a subdirectory of a given path and contains
a file called `metadata.json` will be interpreted as containing a task.
"""

import json
from typing import Any

from etils import epath

from codesembench.api import evaluation_suite
from codesembench.api import task_lib

METADATA_FILENAME = 'metadata.json'


def load_evaluation_suite(
    base_path: epath.Path,
    llm: task_lib.LlmInterface,
    output_dir: epath.Path,
) -> evaluation_suite.EvaluationSuite:
  tasks = load_tasks(base_path)
  return evaluation_suite.EvaluationSuite(llm, tasks, output_dir)


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
