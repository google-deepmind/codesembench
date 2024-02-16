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

"""Base class for evaluation suites."""

import abc
import asyncio
from collections.abc import Sequence
import io
import json

from absl import app
from absl import flags
from etils import epath
import rich
import rich.console
import rich.markdown
import rich.progress

from codesembench.api import task_lib
from codesembench.api import task_loader

_TASKS_DIRECTORY = flags.DEFINE_string(
    'tasks_directory', 'tasks', 'Directory to load the evaluation tasks from.'
)
_OUTPUT_DIRECTORY = flags.DEFINE_string(
    'output_directory', None, 'Path to write the output to.', required=True
)


class NullLlm(task_lib.LlmInterface):
  """Mock LLM that always returns null output."""

  async def generate(
      self,
      prompt: str,
      num_samples: int,
      max_length: int,
      stop_tokens: Sequence[str],
  ) -> Sequence[str]:
    del prompt, num_samples, max_length, stop_tokens
    return ['']


class ProgressBar(abc.ABC):

  @abc.abstractmethod
  def set_total(self, total: float) -> None:
    """Sets the total of the progress bar."""

  def set_state(self, state: float) -> None:
    """Sets the state of the progress bar."""


class EvaluationSuite:
  """A suite knows how to run a set of evaluation tasks and collect results.

  This includes querying an LLM for predicted answers to each of the problems,
  calling the metric functions, and writing the results to a file.

  The suite uses asyncio to run the tasks in parallel.

  Attributes:
    llm: The LLM to use for evaluation.
    output_dir: The directory to write the results to.
    tasks: A list of task_lib.Task objects to run.
  """

  def __init__(
      self,
      llm: task_lib.LlmInterface,
      tasks: Sequence[task_lib.Task],
      output_dir: epath.Path,
  ):
    self._llm = llm
    output_dir.mkdir(parents=True, exist_ok=True)
    self._output_dir = output_dir

    self._tasks = {}
    for task in tasks:
      if task.name in self._tasks:
        raise ValueError(f'Duplicate task name: `{task.name}`.')
      if not task.name.isidentifier():
        raise ValueError(
            f'Invalid task name: `{task.name}`. Must be a valid'
            ' identifier/filename.'
        )
      self._tasks[task.name] = task

  async def _run_all(self, evals_to_run: set[str] | None):
    """Runs all evaluation tasks."""
    with rich.progress.Progress() as progress:
      all_tasks = []
      task_names = []
      for task_name, task in self._tasks.items():
        if evals_to_run is not None and task_name not in evals_to_run:
          continue
        task_log_dir = self._output_dir / task_name
        task_log_dir.mkdir(exist_ok=True)
        all_tasks.append(task.run(self._llm, task_log_dir, progress))
        task_names.append(task_name)
      results = await asyncio.gather(*all_tasks)

    all_results = {}
    with io.StringIO() as sb:
      for task_name, task_results in zip(task_names, results):
        # TODO(mallamanis): Later combine in a more visually pleasing way.
        sb.write(f'\n## {task_name}\n\n')
        all_results[task_name] = task_results
        for metric_name, metric_value in task_results.items():
          if isinstance(metric_value, float):
            sb.write(f'* {metric_name}: {metric_value:.3f}\n')
          else:
            sb.write(f'* {metric_name}: {metric_value}\n')
      markdown_text = sb.getvalue()

    console = rich.console.Console(record=True)
    console.print(markdown_text)

    return markdown_text, all_results

  def run_suite(self, evals_to_run: set[str] | None):
    """Runs the evaluation suite.

    Args:
      evals_to_run: A set with the names of the evaluations to run or `None` to
        run them all.
    """
    summary_text, summary_dict = asyncio.run(self._run_all(evals_to_run))
    with open(self._output_dir / 'eval_summary.md', 'w') as f:
      f.write(summary_text)
    with open(self._output_dir / 'eval_summary.json', 'w') as f:
      json.dump(summary_dict, f)


def load_evaluation_suite(
    base_path: epath.Path,
    llm: task_lib.LlmInterface,
    output_dir: epath.Path,
) -> EvaluationSuite:
  tasks = task_loader.load_tasks(base_path)
  return EvaluationSuite(llm, tasks, output_dir)


def main(argv: Sequence[str]) -> None:
  if len(argv) > 1:
    raise app.UsageError('Too many command-line arguments.')
  suite = load_evaluation_suite(
      _TASKS_DIRECTORY.value,
      NullLlm(),
      _OUTPUT_DIRECTORY.value,
  )
  suite.run_suite(None)


if __name__ == '__main__':
  app.run(main)
