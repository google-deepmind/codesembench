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

"""Evaluation metrics. These are used within Tasks."""

import enum
from typing import Any, Iterable, Sequence


class EvaluationMetrics(enum.Enum):
  PRF1 = 0
  CLUSTER_PRF1 = 1

  def metric_fn(self):
    if self == EvaluationMetrics.PRF1:
      return prf1
    elif self == EvaluationMetrics.CLUSTER_PRF1:
      return cluster_prf1


def prf1(predicted: Iterable[Any], actual: Iterable[Any]) -> dict[str, float]:
  """Compute precision, recall, and F1 for a set of predicted and actual items.

  Here, precision is the proportion of items from predicted that are in actual.
  Recall is the proportion of items from actual that are in predicted.
  F1 is the harmonic mean of precision and recall.

  Args:
    predicted: Iterable of predicted items.
    actual: Iterable of actual items.

  Returns:
    A dictionary with keys 'precision', 'recall', and 'f1'.
  """
  predicted_set = set(predicted)
  actual_set = set(actual)
  n_correct = float(len(predicted_set & actual_set))
  precision = n_correct / len(predicted_set) if len(predicted_set) else 0.0
  recall = n_correct / len(actual_set) if len(actual_set) else 0.0
  if precision + recall > 0.0:
    f1 = 2 * precision * recall / (precision + recall)
  else:
    f1 = 0.0
  return {'precision': precision, 'recall': recall, 'f1': f1}


def sequence_to_pairs(
    clusters: Sequence[Sequence[Any]],
) -> Sequence[tuple[Any, Any]]:
  """Return all pairs of items that occur in the same cluster."""
  result = []
  for cluster in clusters:
    for i in range(len(cluster)):
      for j in range(i + 1, len(cluster)):
        if cluster[i] < cluster[j]:
          tup = (cluster[i], cluster[j])
        else:
          tup = (cluster[j], cluster[i])
        result.append(tup)
  return result


def cluster_prf1(predicted, actual) -> dict[str, float]:
  """Compute precision, recall, and F1 for a predicted and actual clusters.

  Predicted and actual both define different clusterings of the same set.

  Here, precision is the proportion of pairs of items that appear in the same
  cluster in predicted, and also appear in the same cluster in actual.
  Recall is the proportion of pairs of items that appear in the same cluster in
  actual, that also appear in the same cluster in predicted.
  F1 is the harmonic mean of precision and recall.

  Args:
    predicted: Iterable of predicted clusters.
    actual: Iterable of actual clusters.

  Returns:
    A dictionary with keys 'precision', 'recall', and 'f1'.
  """
  predicted_pairs = sequence_to_pairs(predicted)
  actual_pairs = sequence_to_pairs(actual)
  return prf1(set(predicted_pairs), set(actual_pairs))


def macroaverage(
    per_example_results: Sequence[dict[str, float]]
) -> dict[str, float]:
  """Compute macroaverage over evaluation results on individual instances."""
  result = {}
  num_instances = len(per_example_results)
  if not num_instances:
    return result
  keys = per_example_results[0].keys()
  for key in keys:
    result[key] = sum(r[key] for r in per_example_results) / num_instances
  return result
