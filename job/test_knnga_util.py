# Copyright (C) 2020 Juliette Regimbal
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

import json
import knnga_util
import unittest


class TestSelection(unittest.TestCase):
    def setUp(self):
        self.selection = knnga_util.SerializableSelection()

    def test_to_json(self):
        self.selection.setRankSelection(1.5, 1.0)
        self.assertEqual(
            json.loads(self.selection.toJSON()),
            {
                "method": "rank",
                "parameters": {
                    "pressure": 1.5,
                    "exponent": 1.0
                }
            }
        )


class TestReplacement(unittest.TestCase):
    def setUp(self):
        self.replacement = knnga_util.SerializableReplacement()

    def test_to_json(self):
        self.replacement.setSSGAdetTournament(30)
        self.assertEqual(
            json.loads(self.replacement.toJSON()),
            {
                "method": "SSGAdetTournament",
                "parameters": {"tSize": 30}
            }
        )


class TestMutation(unittest.TestCase):
    def setUp(self):
        self.mutation = knnga_util.SerializableMutation()

    def test_to_json(self):
        self.mutation.setGaussMutation(30, 0.0, 1.0, 0.5, 1.0)
        self.assertEqual(
            json.loads(self.mutation.toJSON()),
            [{
                "method": "gauss",
                "parameters": {
                    "numberFeatures": 30,
                    "min": 0.0,
                    "max": 1.0,
                    "sigma": 0.5,
                    "rate": 1.0
                }
            }]
        )


class TestCrossover(unittest.TestCase):
    def setUp(self):
        self.crossover = knnga_util.SerializableCrossover()

    def test_to_json(self):
        self.crossover.setHypercubeCrossover(30, 0.0, 1.0)
        self.assertEqual(
            json.loads(self.crossover.toJSON()),
            [{
                "method": "hypercube",
                "parameters": {
                    "numFeatures": 30,
                    "min": 0.0,
                    "max": 1.0,
                    "alpha": 0.0
                }
            }]
        )


class TestStopCriteria(unittest.TestCase):
    def setUp(self):
        self.sc = knnga_util.SerializableStopCriteria()

    def test_to_json(self):
        self.sc.setMaxFitnessEvals()
        self.assertEqual(
            json.loads(self.sc.toJSON()),
            [{
                "method": "maxFitnessEvals",
                "parameters": {"n": 5000}
            }]
        )
