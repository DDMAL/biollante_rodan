# Copyright (C) 2020 Juliette Regimbal
# SPDX-License-Identifier: GPL-3.0-or-later


from celery.utils.log import get_task_logger
from rodan.jobs.base import RodanTask


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

    logger = get_task_logger(__name__)

    input_port_types = []   # TODO
    output_port_types = []  # TODO

    def get_my_interface(self, inputs, settings):
        raise NotImplementedError

    def validate_my_user_input(self, inputs, settings, user_input):
        raise NotImplementedError

    def run_my_task(self, inputs, settings, outputs):
        raise NotImplementedError

    def my_error_information(self, exc, traceback):
        raise NotImplementedError

    def test_my_task(self, testcase):
        # inputs = {}
        # outputs = {}
        # self.run_my_task(inputs, {}, outputs)
        # result = outputs['out'][0]['resource_path']
        # testcase.assertEqual(result, 'what you expect it to test')
        raise NotImplementedError
