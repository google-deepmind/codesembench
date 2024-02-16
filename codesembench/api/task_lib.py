"""Loads the benchmark tasks as task objects, or as other objects."""

import abc
import asyncio
import dataclasses
import enum
import json
import re
import typing
from typing import Any, List, Sequence, Set

from etils import epath
import rich
import rich.progress

from codesembench.api import metrics


DEFAULT_NUM_SAMPLES = 1
DEFAULT_MAX_LENGTH = 1024
DEFAULT_STOP_TOKENS = ['[eod]']


class TaskType(enum.Enum):
  """Valid types of tasks."""
  PER_FILE = 0
  PER_DIRECTORY = 1


class Language(enum.Enum):
  C = 0
  C_PLUS_PLUS = 1
  PYTHON = 2
  JAVA = 3


class LlmInterface(abc.ABC):
  """Abstract query interface for LLMs."""

  @abc.abstractmethod
  async def generate(
      self,
      prompt: str,
      num_samples: int,
      max_length: int,
      stop_tokens: Sequence[str],
  ) -> Sequence[str]:
    ...

  # A scoring function may be added later if and when it's needed


@dataclasses.dataclass(kw_only=True)
class Task(abc.ABC):
  """Represents a single task in the benchmark.

  A task contains a set of programs that we want the models to do
  semantic analysis on. It should represent one type of semantic question,
  e.g., alias analysis, type inference, etc.

  Attributes:
    name: The name of the task.
    description: A description of the task.
    task_type: The type of task, e.g., per-file or per-directory.
    tags: A list of free-torm tags, which are used to group results.
    language: The programming language for the programs.
    authors: A list of authors for the task.
  """

  # Task metadata
  name: str
  description: str
  task_type: TaskType
  tags: List[str]
  language: Language
  authors: str

  @abc.abstractmethod
  async def run(
      self,
      llm: LlmInterface,
      log_directory: epath.Path,
      progress: rich.progress.Progress,
  ) -> dict[str, Any]:
    """Runs the evaluation task.

    Args:
      llm: The LLM to be queried.
      log_directory: A directory, fully owned by the evaluation, to write any
        outputs.
      progress: A Rich progress bar to display progress.

    Returns:
      A dictionary with the evaluation metrics results of the evaluation.
    """


# TODO: Currently these are per file tasks, but we extend this class
# to handle multi-file tasks.
@dataclasses.dataclass(kw_only=True)
class PropertyPredictionTask(Task):
  """A task that asks the model to predict properties of the code.

  Property prediciton tasks are tasks where the result is
  a list of string properties, e.g., a list of variables that are
  read-only, or a list of functions that are called

  These tasks can be evaluated by comparing the model's prediction to
  a gold standard set of properties that is included in the evaluation.
  The code doesn't need to be executed to perform the evaluation
  (individual methods can choose to execute the code, e.g., if they
  do dynamic analysis.)
  """

  output_type: type[Any]
  file_pattern: str
  answer_path: str = 'answers'
  metric: metrics.EvaluationMetrics = metrics.EvaluationMetrics.PRF1
  data: List['SingleFileProgram'] = dataclasses.field(default_factory=list)
  metric_fn: Any = dataclasses.field(init=False)

  def __post_init__(self):
    self.metric_fn = self.metric.metric_fn()

  async def run(
      self,
      llm: LlmInterface,
      log_directory: epath.Path,
      progress: rich.progress.Progress,
  ) -> dict[str, Any]:
    """Runs the evaluation task.

    Args:
      llm: The LLM to be queried.
      log_directory: A directory, fully owned by the evaluation, to write any
        outputs.
      progress: A Rich progress bar to display progress.

    Returns:
      A dictionary with the results of the evaluation.
    """
    futures = []
    for program in self.data:
      futures.append(self._generate_one_prediction(program, llm))
    predictions = await asyncio.gather(*futures)
    per_program_prf1 = [
        self.metric_fn(result, program.gold_answer)
        for program, result in predictions
    ]
    average_prf1 = metrics.macroaverage(per_program_prf1)
    return average_prf1

  async def _generate_one_prediction(
      self, program: 'SingleFileProgram', llm: LlmInterface
  ) -> tuple['SingleFileProgram', str]:
    """Generates a single prediction for a program.

    Args:
      program: The program to generate a prediction for.
      llm: The LLM to be queried.

    Returns:
      The prediction.
    """
    # TODO: Only works for single file programs right now.
    # TODO: We would need to think about what some of the other eval metrics
    #  mean with num_samples > 1. pass@k is OK, but what about P/R/F1?
    predicted_string = await llm.generate(
        program.source_code,
        num_samples=1,
        max_length=DEFAULT_MAX_LENGTH,
        stop_tokens=DEFAULT_STOP_TOKENS,
    )
    # Be robust in case model predicts single quotes, which is not
    #  valid json.
    json_string = predicted_string[0]
    json_string = json_string.replace("'", '"')
    try:
      predicted_result = json.loads(json_string)
      return program, predicted_result
    except json.JSONDecodeError as e:
      # TODO: Figure out error handling here
      print(f'Could not parse prediction: {json_string}')
      print(e)
      return program, ''

  @classmethod
  def from_metadata(cls, metadata: dict[str, Any]) -> 'PropertyPredictionTask':
    """Creates a Task object from a dict describing its fields.

    The enum objects are created from the strings, if necessary.
    This allows this method to be used from tasks that have been read
    from json.

    Args:
      metadata: Contains values for all of the fields.

    Returns:
      A new Task object.
    """
    if isinstance(metadata['task_type'], str):
      metadata['task_type'] = TaskType[metadata['task_type'].upper()]
    if isinstance(metadata['language'], str):
      metadata['language'] = Language[metadata['language'].upper()]
    if 'output_type' in metadata and isinstance(metadata['output_type'], str):
      metadata['output_type'] = _parse_type(metadata['output_type'])
    if 'metric' in metadata:
      metadata['metric'] = metrics.EvaluationMetrics[metadata['metric'].upper()]
    return cls(**metadata)  # pytype: disable=missing-parameter


# Matches a small subset of Python type annotations.
_TYPE_DESCRIPTION_PATTERN = re.compile(r'^([a-zA-Z]+)(?:\[(.*)\])?$')


def _parse_type(input_str: str) -> type[Any]:
  """Returns a Python type based on a string description of the annotation.

  For example, this maps "List[str]" to the corresponding Python type object.

  This restricts the set of types to "safe" ones that the metric
  functions know how to handle. Right now, this is arbitrarily nested
  containers of strs.

  Args:
    input_str: A string describing the type.

  Returns:
    The Python type object.
  """
  match = _TYPE_DESCRIPTION_PATTERN.match(input_str)
  if match is None:
    raise ValueError(f'Invalid type description: {input_str}')
  origin_type_name = match.group(1)
  type_args_string = match.group(2)
  origin_type = _parse_single_type(origin_type_name)
  if type_args_string:
    # It is possible in the future that we would want to handle types
    # with multiple arguments, like dict. Let's not worry about that
    # for now.
    return origin_type[_parse_type(type_args_string)]
  else:
    return origin_type


def _parse_single_type(input_str: str) -> type[Any]:
  if input_str == 'str':
    return str
  elif input_str == 'list' or input_str == 'List':
    return List
  elif input_str == 'set' or input_str == 'Set':
    return Set
  else:
    raise ValueError(f'Unknown type: {input_str}')


@dataclasses.dataclass(frozen=True, kw_only=True)
class Program:
  """Represents a single datum in the benchmark, which is part of a task."""

  gold_answer: Any
  output_type: type[Any]


@dataclasses.dataclass(frozen=True, kw_only=True)
class SingleFileProgram(Program):
  """A single program in a task, which is contained in a single file."""
  source_code: str
  language: Language


@dataclasses.dataclass(frozen=True, kw_only=True)
class MultiFileProgram(Program):
  """A single program in a task, which is contained in multiple files in a single directory."""
  path: epath.Path
  build_command: str
