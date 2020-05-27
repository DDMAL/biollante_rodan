# Copyright (C) 2020 Juliette Regimbal
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals
from gamera import knnga

import json


class SerializableSelection():
    """
    Extension of gamera.knnga.GASelection that provides
    access to the selection and parameters used.
    """

    def __init__(self):
        self.method = None
        self.parameters = {}
        self.selection = knnga.GASelection()

    def setRandomSelection(self):
        self.method = "random"
        self.parameters = {}
        self.selection.setRandomSelection()

    def setRankSelection(self, pressure=2.0, exponent=1.0):
        self.method = "rank"
        self.parameters = {
            "pressure": pressure,
            "exponent": exponent
        }
        self.selection.setRankSelection(pressure, exponent)

    def setRouletteWheel(self):
        self.method = "roulette"
        self.parameters = {}
        self.selection.setRouletteWheel()

    def setRouletteWheelScaled(self, pressure=2.0):
        self.method = "roulette_scaled"
        self.parameters = {"pressure": pressure}
        self.selection.setRouletteWheelScaled(pressure)

    def setStochUniSampling(self):
        self.method = "stochiastic"
        self.parameters = {}
        self.selection.setStochUniSampling()

    def setTournamentSelection(self, tSize=3):
        self.method = "tournament"
        self.parameters = {"tSize": tSize}
        self.selection.setTournamentSelection(tSize)

    def toJSON(self):
        d = self.__dict__.copy()
        del d['selection']
        return json.dumps(d)

    @staticmethod
    def fromJSON(jsonString):
        d = json.loads(jsonString)
        p = d["parameters"]
        e = SerializableSelection()

        if d["method"] == "random":
            e.setRandomSelection()
        elif d["method"] == "rank":
            if "pressure" in p and "exponent" in p:
                e.setRankSelection(p["pressure"], p["exponent"])
            elif "pressure" in p:
                e.setRankSelection(p["pressure"])
            elif "exponent" in p:
                e.setRankSelection(exponent=p["exponent"])
            else:
                e.setRankSelection()
        elif d["method"] == "roulette":
            e.setRouletteWheel()
        elif d["method"] == "roulette_scaled":
            if "pressure" in p:
                e.setRouletteWheelScaled(p["pressure"])
            else:
                e.setRouletteWheelScaled()
        elif d["method"] == "stochiastic":
            e.setStochUniSampling()
        elif d["method"] == "tournament":
            if "tSize" in p:
                e.setTournamentSelection(p["tSize"])
        return e


class SerializableReplacement():
    """
    Extension of gamera.knnga.GAReplacement that provides
    access to selection method and parameters.
    """
    def __init__(self):
        self.method = None
        self.parameters = {}
        self.replacement = knnga.GAReplacement()

    def setGenerationalReplacement(self):
        self.method = "generational"
        self.parameters = {}
        self.replacement.setGenerationalReplacement()

    def setSSGAdetTournament(self, tSize=3):
        self.method = "SSGAdetTournament"
        self.parameters = {"tSize": tSize}
        self.replacement.setSSGAdetTournament(tSize)

    def setSSGAworse(self):
        self.method = "SSGAworse"
        self.parameters = {}
        self.replacement.setSSGAworse()

    def toJSON(self):
        d = self.__dict__.copy()
        del d['replacement']
        return json.dumps(d)

    @staticmethod
    def fromJSON(jsonString):
        d = json.loads(jsonString)
        e = SerializableReplacement()
        if d["method"] == "generational":
            e.setGenerationalReplacement()
        elif d["method"] == "SSGAdetTournament":
            if "tSize" in d["parameters"]:
                d.setSSGAdetTournament(d["parameters"]["tSize"])
            else:
                d.setSSGAdetTournament()
        elif d["method"] == "SSGAworse":
            d.setSSGAworse()
        return e


class SerializableMutation:
    """
    Extension of gamera.knnga.GAMutation that provides
    access to mutation methods and parameters
    """
    def __init__(self):
        self.methods = []
        self.mutation = knnga.GAMutation()

    def setBinaryMutation(self, rate=0.05, normalize=False):
        self.methods = [x for x in self.methods if x["method"] != "binary"]
        self.methods.append(
            {
                "method": "binary",
                "parameters": {
                    "rate": rate,
                    "normalize": normalize
                }
            }
        )
        self.mutation.setBinaryMutation(rate, normalize)

    def setGaussMutation(self, numberFeatures, min, max, sigma, rate):
        self.methods = [x for x in self.methods if x["method"] != "gauss"]
        self.methods.append(
            {
                "method": "gauss",
                "parameters": {
                    "numberFeatures": numberFeatures,
                    "min": min,
                    "max": max,
                    "sigma": sigma,
                    "rate": rate
                }
            }
        )
        self.mutation.setGaussMutation(numberFeatures, min, max, sigma, rate)

    def setInversionMutation(self):
        if not len([x for x in self.methods if x["method"] == "inversion"]):
            self.methods.append(
                {
                    "method": "inversion",
                    "parameters": {}
                }
            )
        self.mutation.setInversionMutation()

    def setShiftMutation(self):
        if not len([x for x in self.methods if x["method"] == "shift"]):
            self.methods.append(
                {
                    "method": "shift",
                    "parameters": {}
                }
            )
        self.mutation.setShiftMutation()

    def setSwapMutation(self):
        if not len([x for x in self.methods if x["method"] == "swap"]):
            self.methods.append(
                {
                    "method": "swap",
                    "parameters": {}
                }
            )
        self.mutation.setSwapMutation()

    def toJSON(self):
        d = self.__dict__.copy()
        del d['mutation']
        return json.dumps(d)

    @staticmethod
    def fromJSON(jsonString):
        d = json.loads(jsonString)
        e = SerializableMutation()
        for op in d:
            m = op["method"]
            p = op["parameters"]

            if m == "binary":
                if "rate" in p and "normalize" in p:
                    e.setBinaryMutation(p["rate"], p["normalize"])
                elif "rate" in p:
                    e.setBinaryMutation(p["rate"])
                elif "normalize" in p:
                    e.setBinaryMutation(normalize=p["normalize"])
                else:
                    e.setBinaryMutation
            elif m == "gauss":
                e.setGaussMutation(
                    p["numberFeatures"],
                    p["min"],
                    p["max"],
                    p["sigma"],
                    p["rate"]
                )
            elif m == "inversion":
                e.setInversionMutation()
            elif m == "shift":
                e.setShiftMutation()
            elif m == "swap":
                e.setSwapMutation()

        return e


class SerializableCrossover:
    """
    Serializable version of gamera.knnga.GACrossover.
    """
    def __init__(self):
        self.methods = []
        self.crossover = knnga.GACrossover()

    def setHypercubeCrossover(self, numFeatures, min, max, alpha=0.0):
        self.methods = [x for x in self.methods if x["method"] != "hypercube"]
        self.methods.append(
            {
                "method": "hypercube",
                "parameters": {
                    "numFeatures": numFeatures,
                    "min": min,
                    "max": max,
                    "alpha": alpha
                }
            }
        )
        self.crossover.setHypercubeCrossover(numFeatures, min, max, alpha)

    def setNPointCrossover(self, n):
        self.methods = [x for x in self.methods if x["method"] != "nPoint"]
        self.methods.append(
            {
                "method": "nPoint",
                "parameters": {"n": n}
            }
        )
        self.crossover.setNPointCrossover(n)

    def setSBXCrossover(self, numFeatures, min, max, eta=1.0):
        self.methods = [x for x in self.methods if x["method"] != "sbx"]
        self.methods.append(
            {
                "method": "sbx",
                "parameters": {
                    "numFeatures": numFeatures,
                    "min": min,
                    "max": max,
                    "eta": eta
                }
            }
        )
        self.crossover.setSBXCrossover(numFeatures, min, max, eta)

    def setSegmentCrossover(self, numFeatures, min, max, alpha=0.0):
        self.methods = [x for x in self.methods if x["method"] != "segment"]
        self.methods.append(
            {
                "method": "segment",
                "parameters": {
                    "numFeatures": numFeatures,
                    "min": min,
                    "max": max,
                    "alpha": alpha
                }
            }
        )
        self.crossover.setSegmentCrossover(numFeatures, min, max, alpha)

    def setUniformCrossover(self, preference=0.5):
        self.methods = [x for x in self.methods if x["method"] != "uniform"]
        self.methods.append(
            {
                "method": "uniform",
                "parameters": {"preference": preference}
            }
        )
        self.crossover.setUniformCrossover(preference)

    def toJSON(self):
        d = self.__dict__.copy()
        del d['crossover']
        return json.dumps(d)

    @staticmethod
    def fromJSON(jsonString):
        d = json.loads(jsonString)
        e = SerializableCrossover()
        for op in d:
            m = op["method"]
            p = op["parmeters"]

            if m == "hypercube":
                if "alpha" in p:
                    e.setHypercubeCrossover(
                        p["numFeatures"],
                        p["min"],
                        p["max"],
                        p["alpha"]
                    )
                else:
                    e.setHypercubeCrossover(
                        p["numFeatures"],
                        p["min"],
                        p["max"]
                    )
            elif m == "nPoint":
                e.setNPointCrossover(p["n"])
            elif m == "sbx":
                if "eta" in p:
                    e.setSBXCrossover(
                        p["numFeatures"],
                        p["min"],
                        p["max"],
                        p["eta"]
                    )
                else:
                    e.setSBXCrossover(
                        p["numFeatures"],
                        p["min"],
                        p["max"]
                    )
            elif m == "segment":
                if "alpha" in p:
                    e.setSegmentCrossover(
                        p["numFeatures"],
                        p["min"],
                        p["max"],
                        p["alpha"]
                    )
                else:
                    e.setSegmentCrossover(
                        p["numFeatures"],
                        p["min"],
                        p["max"]
                    )
            elif m == "uniform":
                if "preference" in p:
                    e.setUniformCrossover(p["preference"])
                else:
                    e.setUniformCrossover()
        return e


class SerializableStopCriteria:
    """
    Serializable version of gamera.knnga.GAStopCriteria
    """
    def __init__(self):
        self.methods = []
        self.sc = knnga.GAStopCriteria()

    def setBestFitnessStop(self, optimum=1.0):
        self.methods = [x for x in self.methods
                        if x["method"] != "bestFitness"]
        self.methods.append(
            {
                "method": "bestFitness",
                "parameters": {"optimum": optimum}
            }
        )
        self.sc.setBestFitnessStop(optimum)

    def setMaxFitnessEvals(self, n=5000):
        self.methods = [x for x in self.methods
                        if x["method"] != "maxFitnessEvals"]
        self.methods.append(
            {
                "method": "maxFitnessEvals",
                "parameters": {"n": n}
            }
        )
        self.sc.setMaxFitnessEvals(n)

    def setMaxGenerations(self, n=100):
        self.methods = [x for x in self.methods
                        if x["method"] != "maxGenerations"]
        self.methods.append(
            {
                "method": "maxGenerations",
                "parameters": {"n": n}
            }
        )
        self.sc.setMaxGenerations(n)

    def setSteadyStateStop(self, minGens=40, noChangeGens=10):
        self.methods = [x for x in self.methods
                        if x["method"] != "steadyState"]
        self.methods.append(
            {
                "method": "steadyState",
                "parameters": {
                    "minGens": minGens,
                    "noChangeGens": noChangeGens
                }
            }
        )
        self.sc.setSteadyStateStop(minGens, noChangeGens)

    def toJSON(self):
        d = self.__dict__.copy()
        del d["sc"]
        return json.dumps(d)

    @staticmethod
    def fromJSON(jsonString):
        d = json.loads(jsonString)
        e = SerializableStopCriteria()
        for op in d:
            m = op["method"]
            p = op["parameters"]

            if m == "bestFitness":
                if "optimum" in p:
                    e.setBestFitnessStop(p["optimum"])
                else:
                    e.setBestFitnessStop()
            elif m == "maxFitnessEvals":
                if "n" in p:
                    e.setMaxFitnessEvals(p["n"])
                else:
                    e.setMaxFitnessEvals()
            elif m == "maxGenerations":
                if "n" in p:
                    e.setMaxGenerations(p["n"])
                else:
                    e.setMaxGenerations()
            elif m == "steadyState":
                if "minGens" in p and "noChangeGens" in p:
                    e.setSteadyStateStop(p["minGens"], p["noChangeGens"])
                elif "minGens" in p:
                    e.setSteadyStateStop(p["minGens"])
                elif "noChangeGens" in p:
                    e.setSteadyStateStop(noChangeGens=p["noChangeGens"])
                else:
                    e.setSteadyStateStop()
        return e
