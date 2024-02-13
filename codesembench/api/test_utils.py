"""Utilities used in the unit tests."""

from typing import Sequence

from etils import epath

from codesembench.api import task_lib
from google3.pyglib import resources


def get_tasks_path():
  return (
      epath.Path(resources.GetARootDirWithAllResources())
      / "google3/experimental/users/charlessutton/codesembench/codesembench/api/testdata/tasks"
  )


def _get_task_by_name(
    tasks: Sequence[task_lib.Task], name: str
) -> task_lib.Task:
  for task in tasks:
    if task.name == name:
      return task
  raise ValueError(f"Task {name} not found.")


MOCK_LLM_EXAMPLES = [
    # Below comments compare to the expected outputs of simple_c_alias.
    "[['p', 'm0'], ['m1']]",  # Exactly right.
    "[['p0', 'p'], ['p1']]",  # P=1.0, R=0.5
    # P=0.2, R=0.3333
    "[['p0', 'quxx'], ['burble', 'bloop'], ['p1', 'p[0]', 'fizz']]",
    "[]",
    "['result']",
]


class MockLlm(task_lib.LlmInterface):
  """Mock LLM for unit tests."""

  def __init__(self):
    self._examples = MOCK_LLM_EXAMPLES
    self.i = 0

  async def generate(
      self,
      prompt: str,
      num_samples: int,
      max_length: int,
      stop_tokens: Sequence[str],
  ) -> Sequence[str]:
    del prompt, num_samples, max_length, stop_tokens
    result = self._examples[self.i]
    self.i += 1
    return [result]
