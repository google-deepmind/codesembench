# CodeSemBench: Measuring LLM Code Reasoning

CodeSemBench is a proposal for a collaborative benchmark designed to test how
well current code language models can perform in reasoning about programs.

The CodeSemBench benchmark consists of a set of tasks, where each task is
designed to test a specific kind of semantic reasoning, e.g., one task might
test alias analysis in C. Each task contain a set of programs that we want the
models to analyze, as well as the correct results of the analyzer.

The overall structure of this repository is inspired by the
[BIG-bench](https://github.com/google/BIG-bench) repository. Each task is
represented as a subdirectory in this repository, so the set of programs in the
benchmark are be version controlled.

## Running the benchmark

To run the benchmark tasks, use this command line:

```
python api/evaluation_suite.py \
    --task_directory=tasks/ \
    --output_directory=$HOME/codesembench_output/
```

This will output the evaluation metrics for each task into the output directory
in JSON and Markdown format.

## Adding new tasks

To add a new task, create a directory in the `tasks/` directory with the name of
the task. Add a meta-data file, as described in the task metadata section,
below.

For a per file task, each data point in a benchmark is a program where that we
want to run an analysis one, and where we know the correct answer. Create one
file for each program that you want to include in the task, and then a different
file for the correct answer. Right now, the evaluation running is set up for
zero-shot prompts, i.e., each program contains a comment at the top indicating
what program analysis the LLM would do. It shouldn't be too hard to extend the
framework to support LLMs that prefer few shot prompts.

The test runner code will look for all subdirectories in the `tasks` directory
that contain a metadata file, and create one evaluation task for each metadata
file that it finds.

TODO: The loading framework can be extended pretty easily to handle tasks where
each program takes up multiple files. This would require creating a new subclass
of `Program` and of `Task` in `api.task_lib`, as well as creating functions in
`task_loader` to be able to load such programs.

## Metrics

As far as possible, it is a good to make sure tasks rely on a small set of
evaluation metrics, like precision and recall. This way it is easier to average
together scores on the benchmark tasks into a single macro-score. Currently
supported metrics are listed in `metrics.py`.

## Task metadata

Each task should contain a file called `metadata.json`, which provides the
information that the evaluation runner needs to load and evaluate the models on
the task. This file should contain a single dictionary with the following keys
(keys are all strings):

*   "name": A string name for the task.
*   "description": A short string describing what the task measures and why it
    is important, e.g., "Simple programs to list the aliases of a variable in
    C.",
*   "language": What programming language is primarily tested. This must be one
    of the keys of the `task_lib.Language` enum.
*   "authors": String describing author names and POC for questions.
*   "output_type": The Python type of the correct answer. e.g., if the outputs
    are a list of variable names that escape a function, then this would be
    `List[str]`.
*   "metric": What evaluation metric should be called on the results. This must
    be one of the members of the `metrics.EvaluationMetrics` enum.
*   "tags": (list of strings) A list of freeform tags. It is intended that these
    tags could be used for organizing an automatically-generated report.
*   "benchmark_type": A string describing the "type" of benchmark, which
    determines how programs are read from disk. This should be one of the
    entries of the `task_lib.TaskType` enum.

Per file benchmarks are those where every program in the task is contained in a
single file, and the answer is also read from a single file. These benchmarks
use the following additional metadata fields:

*   "file_glob": All files that match this glob will be treated as files in the
    task.
*   "gold_answer_pattern": Python f-string. For each program in the task, the
    file name will be fed to this f-string to come up with the file name for the
    correct solution to that task.
