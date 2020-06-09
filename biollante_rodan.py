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

    base = None
    selection = None
    replacement = None
    mutation = None
    crossover = None
    stop_criteria = None
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
            "stop_criteria": json.loads(settings["@stop_criteria"]),
            "optimizer": settings["@results"]
        }
        return "index.html", context

    def validate_my_user_input(self, inputs, settings, user_input):
        assert settings["@state"] == STATE_NOT_OPTIMIZING, \
            "Must not be optimizing! State is %s" % str(settings["@state"])

        # Start the optimization process
        if user_input["method"] == "start":
            try:
                self.setup_optimizer(user_input, settings["@num_features"])
            except Exception as e:
                raise self.ManualPhaseException(str(e))

            d = self.knnga_dict()
            d["@state"] = STATE_OPTIMIZING
            d["@settings"] = settings["@settings"]
            return d

        # Save the latest classifier version and finsh job.
        elif user_input["method"] == "finish":
            return {
                "@state": STATE_FINISHING,
                "@settings": settings["@settings"]
            }
        else:
            self.logger.warn("Unknown method: %s" % user_input["method"])
            return {}

    def run_my_task(self, inputs, settings, outputs):
        if "@state" not in settings:
            settings["@state"] = STATE_INIT

        if settings["@state"] == STATE_INIT:
            self.logger.info("State: Init")

            with NTF(suffix=".xml") as temp:
                self.logger.info(temp.name)
                # Gamera fails to load files without xml extension.
                shutil.copy2(
                    inputs["kNN Training Data"][0]["resource_path"],
                    temp.name
                )
                classifier = knn.kNNNonInteractive(temp.name)

            with NTF() as temp:
                classifier.save_settings(temp.name)
                temp.flush()
                temp.seek(0)
                settings["@settings"] = temp.read()

            # Preserve the number of features for certain kinds
            # of operations the GA optimizer might perform.
            settings["@num_features"] = classifier.num_features

            self.base = knnga.GABaseSetting()
            self.selection = util.SerializableSelection()
            self.replacement = util.SerializableReplacement()
            self.mutation = util.SerializableMutation()
            self.crossover = util.SerializableCrossover()
            self.stop_criteria = util.SerializableStopCriteria()

            settings["@state"] = STATE_NOT_OPTIMIZING

        if settings["@state"] == STATE_NOT_OPTIMIZING:
            self.logger.info("State: Not Optimizing")

            # Create set of parameters for template
            d = self.knnga_dict()
            d["@state"] = STATE_NOT_OPTIMIZING
            d["@settings"] = settings["@settings"]
            return self.WAITING_FOR_INPUT(d)

        elif settings["@state"] == STATE_OPTIMIZING:
            self.logger.info("State: Optimizing")
            self.load_from_settings(settings)

            # Load data
            with NTF(suffix=".xml") as temp:
                shutil.copy2(
                    inputs["kNN Training Data"][0]["resource_path"],
                    temp.name
                )
                classifier = knn.kNNNonInteractive(temp.name)

            # Load selection and weights
            with NTF(suffix=".xml") as temp:
                temp.write(settings["@settings"])
                temp.flush()
                classifier.load_settings(temp.name)

            self.optimizer = knnga.GAOptimization(
                classifier,
                self.base,
                self.selection.selection,
                self.crossover.crossover,
                self.mutation.mutation,
                self.replacement.replacement,
                self.stop_criteria.sc,
                knnga.GAParallelization(True, 4)
            )

            assert isinstance(self.optimizer, knnga.GAOptimization), \
                "Optimizer is %s" % str(type(self.optimizer))

            try:
                self.optimizer.startCalculation()
            except Exception as e:
                self.logger.error(e)
                self.logger.error("Failed to start optimizing!")
                return False

            # Wait for optimization to finish
            while self.optimizer.status:
                sleep(30000)    # 30 seconds
                self.logger.info(self.optimizer.monitorString)

            # This is necessary since the classifier object isn't persistent
            settings = self.knnga_dict()

            with NTF() as temp:
                classifier.save_settings(temp.name)
                temp.flush()
                temp.seek(0)
                settings["@settings"] = temp.read()

            settings["@state"] = STATE_NOT_OPTIMIZING
            return self.WAITING_FOR_INPUT(settings)

        else:   # Finish
            self.logger.info("State: Finishing")
            with open(
                outputs["GA Optimized Classifier"][0]["resource_path"], 'w'
            ) as f:
                f.write(settings["@settings"])
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
        """
        Return a dictionary object with serializations
        of settings objects and a result summary (if any).
        """
        return {
            "@base": util.base_to_json(self.base),
            "@selection": self.selection.toJSON(),
            "@replacement": self.replacement.toJSON(),
            "@mutation": self.mutation.toJSON(),
            "@crossover": self.crossover.toJSON(),
            "@stop_criteria": self.stop_criteria.toJSON(),
            "@results": None if self.optimizer is None else {
                "generation": self.optimizer.generation,
                "bestFitness": self.optimizer.bestFitness,
            }
        }

    def load_from_settings(self, settings):
        self.base = util.json_to_base(settings["@base"])
        self.selection = util.SerializableSelection.fromJSON(
            settings["@selection"]
        )
        self.replacement = util.SerializableReplacement.fromJSON(
            settings["@replacement"]
        )
        self.mutation = util.SerializableMutation.fromJSON(
            settings["@mutation"]
        )
        self.crossover = util.SerializableCrossover.fromJSON(
            settings["@crossover"]
        )
        self.stop_criteria = util.SerializableStopCriteria.fromJSON(
            settings["@stop_criteria"]
        )

    def setup_optimizer(self, options, num_features):
        """
        Ensure we have the info necessary to run GA optimization.
        """
        assert num_features is not None, "NUM FEATURES"
        base = util.dict_to_base(options["base"])
        selection = util.SerializableSelection.from_dict(
            options["selection"]
        )
        replacement = util.SerializableReplacement.from_dict(
            options["replacement"]
        )
        mutation = util.SerializableMutation.from_dict(
            options["mutation"],
            num_features
        )
        crossover = util.SerializableCrossover.from_dict(
            options["crossover"],
            num_features
        )
        stop_criteria = util.SerializableStopCriteria.from_dict(
            options["stop_criteria"]
        )

        assert selection.method is not None, "No selection method"
        assert replacement.method is not None, "No replacement method"
        assert len(mutation.methods) > 0, "No mutation methods"
        assert len(crossover.methods) > 0, "No crossover methods"
        assert len(stop_criteria.methods) > 0, "No stop criteria"

        self.base, self.selection, self.replacement, self.mutation, \
            self.crossover, self.stop_criteria = base, selection,   \
            replacement, mutation, crossover, stop_criteria
