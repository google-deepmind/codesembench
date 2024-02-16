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

from setuptools import setup, find_packages

setup(
    name='codesembench', 
    version='0.0.1',
    python_requires='>3.10',
    description='Semantic benchmark for code LLMs.',
    author='Google LLC',
    author_email='your_email@example.com',
    packages=find_packages(),  # Automatically finds packages
    install_requires=[
	"epath",
	"pytest"
    ]
)
