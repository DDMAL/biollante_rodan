# Copyright (C) 2020 Juliette Regimbal
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from celery.utils.log import get_task_logger
from gamera import knn, knnga
from rodan.jobs.base import RodanTask
from tempfile import NamedTemporaryFile as NTF
from time import sleep

import json
import knnga_util as util
import shutil


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
        self.logger.info(settings)
        context = {
            "base": json.loads(settings["@base"]),
            "selection": json.loads(settings["@selection"]),
            "replacement": json.loads(settings["@replacement"]),
            "mutation": json.loads(settings["@mutation"]),
            "crossover": json.loads(settings["@crossover"]),
            "stop_critera": json.loads(settings["@stop_criteria"]),
            "optimizer": settings["@optimizer"]
        }
        return "index.html", context

    def validate_my_user_input(self, inputs, settings, user_input):
        assert settings["@state"] == STATE_NOT_OPTIMIZING, \
            "Must not be optimizing! State is %s" % str(settings["@state"])
        if user_input["method"] == "start":
            try:
                self.setup_optimizer(user_input)
            except AssertionError as e:
                return self.WAITING_FOR_INPUT({}, response=str(e))

            d = self.knnga_dict()
            d["@state"] = STATE_OPTIMIZING
            return d

        elif user_input["method"] == "finish":
            assert self.optimizer is not None, "Optimizer is unset!"
            return {"@state": STATE_FINISHING}
        else:
            self.logger.warn("Unknown method: %s" % user_input["method"])

    def run_my_task(self, inputs, settings, outputs):
        if "@state" not in settings:
            settings["@state"] = STATE_INIT

        if settings["@state"] == STATE_INIT:
            self.logger.info("State: Init")
            # File must have xml extension because ???
            # Otherwise Gamera will raise an error.
            with NTF(suffix=".xml") as temp:
                self.logger.info(temp.name)
                shutil.copy2(
                    inputs["kNN Training Data"][0]["resource_path"],
                    temp.name
                )
                self.classifier = knn.kNNNonInteractive(temp.name)

            self.base = knnga.GABaseSetting()
            self.selection = util.SerializableSelection()
            self.replacement = util.SerializableReplacement()
            self.mutation = util.SerializableMutation()
            self.crossover = util.SerializableCrossover()
            self.stop_critera = util.SerializableStopCriteria()

            settings["@state"] = STATE_NOT_OPTIMIZING

        if settings["@state"] == STATE_NOT_OPTIMIZING:
            self.logger.info("State: Not Optimizing")
            # Create set of parameters for template
            d = self.knnga_dict()
            d["@state"] = STATE_NOT_OPTIMIZING
            return self.WAITING_FOR_INPUT(d)
        elif settings["@state"] == STATE_OPTIMIZING:
            self.logger.info("State: Optimizing")
            # Wait for optimization to finish
            while self.optimizer.status:
                sleep(30000)    # 30 seconds
            # Get info from optimizer
            settings["@state"] = STATE_NOT_OPTIMIZING
            return self.WAITING_FOR_INPUT()
        else:   # Finish
            self.logger.info("State: Finishing")
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

    def knnga_dict(self):
        return {
            "@base": util.base_to_json(self.base),
            "@selection": self.selection.toJSON(),
            "@replacement": self.replacement.toJSON(),
            "@mutation": self.mutation.toJSON(),
            "@crossover": self.crossover.toJSON(),
            "@stop_criteria": self.stop_critera.toJSON(),
            "@optimizer": None if not self.optimizer else {
                "generation": self.optimizer.generation,
                "bestFitness": self.optimizer.bestFitness
            }
        }

    def setup_optimizer(self, options):
        base = util.json_to_base(options["base"])
        selection = util.SerializableSelection \
            .fromJSON(options["selection"])
        replacement = util.SerializableReplacement \
            .fromJSON(options["replacement"])
        mutation = util.SerializableMutation.fromJSON(options["mutation"])
        crossover = util.SerializableCrossover \
            .fromJSON(options["crossover"])
        stop_criteria = util.SerializableStopCriteria \
            .fromJSON(options["stop_critera"])

        # Add assertions to ensure valid optimizing can occur!

        self.base, self.selection, self.replacement, self.mutation, \
            self.crossover, self.stop_critera = base, selection,    \
            replacement, mutation, crossover, stop_criteria

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
