# Copyright (C) 2020 Juliette Regimbal
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from celery.utils.log import get_task_logger
from gamera import knn, knnga
from rodan.jobs.base import RodanTask
from time import sleep

import knnga_util as util


STATE_INIT = 0
STATE_NOT_OPTIMIZING = 1
STATE_OPTIMIZING = 2
STATE_FINISHING = 3


class BiollanteRodan(RodanTask):
    name = "Biollante"
    author = "Juliette Regimbal"
    description = "GA Optimizer for kNN Classifiers"
    settings = {
        "job_queue": "Python2"  # This is due to using gamera
    }
    enabled = True
    category = "Optimization"
    interactive = True

    classifier = None
    base = None
    selection = None
    replacement = None
    mutation = None
    crossover = None
    stop_critera = None
    optimizer = None

    logger = get_task_logger(__name__)

    input_port_types = [
        {
            "name": "kNN Training Data",
            "minimum": 1,
            "maximum": 1,
            "resource_types": ["application/gamera+xml"]
        }
    ]
    output_port_types = [
        {
            "name": "GA Optimized Classifier",
            "minimum": 1,
            "maximum": 1,
            "resource_types": ["application/gamera+xml"]
        }
    ]

    def get_my_interface(self, inputs, settings):
        raise NotImplementedError

    def validate_my_user_input(self, inputs, settings, user_input):
        if user_input["method"] == "start":
            if settings["@state"] == STATE_NOT_OPTIMIZING:
                pass
            pass
        elif user_input["method"] == "finish":
            pass
        raise NotImplementedError

    def run_my_task(self, inputs, settings, outputs):
        if "@state" not in settings:
            settings["@state"] = STATE_INIT

        if settings["@state"] == STATE_INIT:
            self.classifier = knn.kNNNonInteractive(
                inputs["kNN Training Data"][0]["resource_path"]
            )

            self.base = knnga.GABaseSetting()
            self.selection = util.SerializableSelection()
            self.replacement = util.SerializableReplacement()
            self.mutation = util.SerializableMutation()
            self.crossover = util.SerializableCrossover()
            self.stop_critera = util.SerializableStopCriteria()

        if settings["@state"] == STATE_NOT_OPTIMIZING:
            # Create set of parameters for template
            return self.WAITING_FOR_INPUT({
                "@state": STATE_NOT_OPTIMIZING,
                "@base": util.base_to_json(self.base),
                "@selection": self.selection.toJSON(),
                "@replacemnt": self.replacement.toJSON(),
                "@mutation": self.mutation.toJSON(),
                "@crossover": self.crossover.toJSON(),
                "@stop_criteria": self.stop_critera.toJSON(),
                "@optimizer": None if not self.optimizer else {
                    "generation": self.optimizer.generation,
                    "bestFitness": self.optimizer.bestFitness
                }
            })
        elif settings["@state"] == STATE_OPTIMIZING:
            # Wait for optimization to finish
            while self.optimizer.status:
                sleep(30000)    # 30 seconds
            # Get info from optimizer
            settings["@state"] = STATE_NOT_OPTIMIZING
            return self.WAITING_FOR_INPUT()
        else:   # Finish
            self.classifier.to_xml_filename(
                outputs["GA Optimized Classifier"][0]["resource_path"]
            )
            return True

    def my_error_information(self, exc, traceback):
        raise NotImplementedError

    def test_my_task(self, testcase):
        # inputs = {}
        # outputs = {}
        # self.run_my_task(inputs, {}, outputs)
        # result = outputs['out'][0]['resource_path']
        # testcase.assertEqual(result, 'what you expect it to test')
        raise NotImplementedError

    def create_context_dict(self):
        pass

    def setup_optimizer(self, options):
        self.base = util.json_to_base(options["base"])
        self.selection = util.SerializableSelection \
            .fromJSON(options["selection"])
        self.replacement = util.SerializableReplacement \
            .fromJSON(options["replacement"])
        self.mutation = util.SerializableMutation.fromJSON(options["mutation"])
        self.crossover = util.SerializableCrossover \
            .fromJSON(options["crossover"])
        self.stop_criteria = util.SerializableStopCriteria \
            .fromJSON(options["stopCriteria"])

        parallel = knnga.GAParallelization()
        parallel.mode = True
        parallel.thredNum = 4   # sic

        self.optimizer = knnga.GAOptimizer(
            self.classifier,
            self.base,
            self.selection,
            self.crossover,
            self.mutation,
            self.replacement,
            self.stop_criteria,
            parallel
        )
