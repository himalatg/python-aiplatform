# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

SYSTEM_RUN = "system.Run"
SYSTEM_EXPERIMENT = "system.Experiment"
SYSTEM_EXPERIMENT_RUN = "system.ExperimentRun"
SYSTEM_PIPELINE = "system.Pipeline"
SYSTEM_PIPELINE_RUN = "system.PipelineRun"
SYSTEM_METRICS = "system.Metrics"

_EXPERIMENTS_V2_SYSTEM_RUN = "google_dev.SystemRun"
_EXPERIMENTS_V2_SYSTEM_RUN_SCHEMA_TITLE = "google-dev-vertex-system-run-v0-0-1"
_EXPERIMENTS_V2_TENSORBOARD_RUN = "google_dev.VertexTensorboardRun"

_DEFAULT_SCHEMA_VERSION = "0.0.1"
_EXPERIMENT_V2_SCHEMA_VERSION = "0.0.2"

SCHEMA_VERSIONS = {
    SYSTEM_RUN: _DEFAULT_SCHEMA_VERSION,
    SYSTEM_EXPERIMENT: _DEFAULT_SCHEMA_VERSION,
    SYSTEM_EXPERIMENT_RUN: _DEFAULT_SCHEMA_VERSION,
    SYSTEM_PIPELINE: _DEFAULT_SCHEMA_VERSION,
    SYSTEM_METRICS: _DEFAULT_SCHEMA_VERSION,
}

# The EXPERIMENT_METADATA is needed until we support context deletion in backend service.
# TODO: delete EXPERIMENT_METADATA once backend supports context deletion.
_PARAM_KEY = '_params'
_METRIC_KEY = '_metrics'
_STATE_KEY = '_state'
EXPERIMENT_METADATA = {'experiment_deleted':False}

PIPELINE_PARAM_PREFIX = "input:"

TENSORBOARD_CUSTOM_JOB_EXPERIMENT_FIELD = "tensorboard_link"
