#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from ops.testing import Harness
from src.literals import Role, Status

from charm import KafkaCharm
from literals import (
    CONTAINER,
    SUBSTRATE,
)

pytestmark = pytest.mark.partitioner

logger = logging.getLogger(__name__)


CONFIG = str(yaml.safe_load(Path("./config.yaml").read_text()))
ACTIONS = str(yaml.safe_load(Path("./actions.yaml").read_text()))
METADATA = str(yaml.safe_load(Path("./metadata.yaml").read_text()))


@pytest.fixture
def harness() -> Harness:
    harness = Harness(KafkaCharm, meta=METADATA, actions=ACTIONS, config=CONFIG)

    if SUBSTRATE == "k8s":
        harness.set_can_connect(CONTAINER, True)

    harness._update_config({"role": "partitioner"})
    harness.begin()
    return harness


def test_start_with_correct_role(harness: Harness):
    assert harness.charm.config["role"] == Role.PARTITIONER


def test_install_blocks_snap_install_failure(harness: Harness):
    """Checks unit goes to BlockedStatus after snap failure on install hook."""
    with patch("workload.KafkaWorkload.install", return_value=False):
        harness.charm.on.install.emit()
        assert harness.charm.unit.status == Status.SNAP_NOT_INSTALLED.value.status


def test_ready_to_start_not_implemented(harness: Harness):
    harness.charm.on.start.emit()
    assert harness.charm.unit.status == Status.NOT_IMPLEMENTED.value.status
