"""Utilities used in the unit tests."""

from typing import Sequence

from etils import epath

from codesembench.api import task_lib


def get_tasks_path():
  return (
      epath.Path(__file__).parent
      / "testdata/tasks"
  )


def _get_task_by_name(
    tasks: Sequence[task_lib.Task], name: str
) -> task_lib.Task:
  for task in tasks:
    if task.name == name:
      return task
  raise ValueError(f"Task {name} not found.")


# This lets us produced canned answers for the prompts in the test data,
# so we know the correct precision and recall.
# This is a dict where the keys are strings that uniquely occur in different test programs,
# and the value is what we want the mocked LM to return if it sees that string.
MOCK_LLM_EXAMPLES = {
    # Below comments compare to the expected outputs of simple_c_alias.
    # alias0.c: exactly right
    "int fn (int x, int y, int *p) {": "[['p', 'm0'], ['m1']]",  
    # alias1.c: P=1.0, R=0.5
    "// This is test alias2.c": "[['p0', 'p'], ['p1']]", 
    # alias2.c: P=0.2, R=0.3333
    "// This is test alias3.c": "[['p0', 'quxx'], ['burble', 'bloop'], ['p1', 'p[0]', 'fizz']]",
}


class MockLlm(task_lib.LlmInterface):
  """Mock LLM for unit tests."""

  def __init__(self):
    self._examples = MOCK_LLM_EXAMPLES

  async def generate(
      self,
      prompt: str,
      num_samples: int,
      max_length: int,
      stop_tokens: Sequence[str],
  ) -> Sequence[str]:
    del num_samples, max_length, stop_tokens
    # If we recognize the prompt, return the canned answer, 
    # else return "['']"
    result = ''
    for k in self._examples.keys():
      if k in prompt:
        result = self._examples[k]
    return [result]
