#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

A ValueStore is used to save the state information of the observed or calculated state.
'''
import copy
import json
import logging
import os
import pickle
import time
from collections import defaultdict

from LoggerUtilities import initializeLogging
from StateManagerUtilities import formatTimestamp

logger = logging.getLogger(__name__)

LAST_DUMP_FILENAME = "valueStoreDump"
AUTOSAVE_FILENAME = "valueStoreAutosaveDump"
DUMP_PATH = "/data/valueDumps/"


class ValueNotStoredException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def pickleableLambdaSubstitute():
    return []


class ValueStore():
    def __init__(self, name, description="", initialValues=None):
        """
        Initialize a ValueStore.
        :param name: Name of ValueStore.
        :param description: Description of ValueStore.
        :param initialValues: Initial values for store as dictionary
        """
        self.name = name
        self.description = description
        self.store = initialValues if type(initialValues) == dict else dict()
        self.history = defaultdict(pickleableLambdaSubstitute)

    def updateValue(self, name, value, timestamp=None):
        """
        Update a value in the ValueStore.
        :param name: Reference key
        :param value: New value
        :param timestamp: Timestamp of change (if available)
        """
        if not timestamp:
            timestamp = time.time()
        if self.store.has_key(name):
            self.history[name].append(self.store[name])
        self.store[name] = (value, timestamp, True)

    def invalidateValue(self, name):
        """
        Invalidates a value in the ValueStore.
        :param name: Reference key
        """
        if self.store.has_key(name):
            self.store[name] = (self.store[name][0], self.store[name][1], False)

    def retrieveValue(self, name, retrieveInvalidValues=False):
        """
        Request a value from the value store.
        Throws ValueNotStoredException if value is not in ValueStore.
        :param name: Reference key
        :param retrieveInvalidValues: True if also invalidated values should be returned, ValueNotStoredException otherwise
        :return: Stored value
        """
        if not self.store.has_key(name):
            raise ValueNotStoredException("%s not in ValueStore." % name)
        if not retrieveInvalidValues and not self.store[name][2]:
            raise ValueNotStoredException("%s in ValueStore, but was invalidated." % name)
        return self.store[name][0]

    def retrieveAge(self, name):
        """
        Request the age of the value
        Throws ValueNotStoredException if value is not in ValueStore.
        :param name: Reference key
        :return: Age of value
        """
        if not self.store.has_key(name):
            raise ValueNotStoredException("%s not in ValueStore." % name)
        return time.time() - self.store[name][1]

    def retrieveValueBefore(self, name, timestamp):
        """
        Request a value from the value store before a given timestamp.
        Throws ValueNotStoredException if no value is known by history of ValueStore before that time.
        :param name: Reference key
        :param timestamp: Timestamp
        :return: Stored value
        """
        if not self.store.has_key(name):
            raise ValueNotStoredException("%s not in ValueStore." % name)
        if not self.store[name][2]:
            raise ValueNotStoredException("%s in ValueStore, but was invalidated." % name)
        if self.store[name][1] < timestamp:
            return self.store[name][0]
        else:
            latestValue = None
            for v in sorted(self.history[name], key=lambda (a, b, c): b):
                if v[1] > timestamp:
                    break
                latestValue = v[0]
            if latestValue:
                return latestValue
            else:
                raise ValueNotStoredException("%s not in ValueStore at time %d." % (name, timestamp))

    def hasValue(self, name):
        """
        Check whether reference is known to ValueStore.
        :param name: Reference key
        :return: True if value is stored for reference key
        """
        return self.store.has_key(name)

    def getCopy(self, newName=None):
        """
        Generate a deep copy of the ValueStore.
        :param newName: Name of new ValueStore
        :return: New ValueStore object
        """
        copied = copy.deepcopy(self)
        if newName:
            copied.name = newName
        return copied

    def _printKeyInfo(self, key):
        """
        Prints value information about a stored value.
        :param key: Reference key
        """
        valid = "(invalidated)" if not self.store[key][2] else ""
        if type(self.store[key]) == float:
            logger.info("\t%s[%s]: %8f %s" % (self.name, key, self.store[key][0], valid))
        else:
            logger.info("\t%s[%s]: %s %s" % (self.name, key, self.store[key][0], valid))

    def compareTo(self, otherValueStore):
        """
        Compares two ValueStores.
        :param otherValueStore: Other ValueStore
        """
        logger.info("Comparing ValueStore %s with ValueStore %s." % (self.name, otherValueStore.name))
        keys1 = set(self.store.keys())
        keys2 = set(otherValueStore.store.keys())
        added = keys1 - keys2
        removed = keys2 - keys1
        intersection = keys1.intersection(keys2)
        modified = {key for key in intersection if self.store[key] <> otherValueStore.store[key]}
        equal = {key for key in intersection if self.store[key] == otherValueStore.store[key]}
        logger.info("Equal key-values:")
        for k in equal:
            self._printKeyInfo(k)
        logger.info("Keys only in %s:" % self.name)
        for k in added:
            self._printKeyInfo(k)
        logger.info("Keys only in %s:" % otherValueStore.name)
        for k in removed:
            otherValueStore._printKeyInfo(k)
        logger.info("Modified key-values:")
        for k in modified:
            logger.info(" Key %s" % k)
            self._printKeyInfo(k)
            otherValueStore._printKeyInfo(k)
            logger.info("")

    def printCurrentState(self):
        """Print the currently stored values."""
        logger.info("Currently stored values:")
        for k, v in sorted(self.store.iteritems(), key=lambda (a, b): a):
            valid = "(invalidated)" if not v[2] else ""
            if type(v[0]) == float:
                logger.info("\t%-10s:%8f %s (since %s)" % (k, v[0], valid, formatTimestamp(v[1])))
            else:
                logger.info("\t%-10s:%s %s (since %s)" % (k, v[0], valid, formatTimestamp(v[1])))
        logger.info("Total stored values: %d" % len(self.store))

    def printFullHistory(self):
        """Print the value history."""
        logger.debug("Full value history:")
        for n in sorted(self.store.keys()):
            self.printHistory(n)
        logger.debug("Total history entries: %d" % sum([len(self.history[n]) for n in self.store.keys()]))

    def printHistory(self, name):
        """
        Print the value history for a specific value.
        :param name: Reference key
        """
        if not self.store.has_key(name):
            logger.debug("No value found for %s." % name)
        else:
            logger.debug("Value history for %s:" % name)
            if type(self.store[name][0]) == float:
                logger.debug("\t%s: %8f (current)" % (formatTimestamp(self.store[name][1]), self.store[name][0]))
            else:
                logger.debug("\t%s: %s (current)" % (formatTimestamp(self.store[name][1]), self.store[name][0]))
            for v, t, valid in sorted(self.history[name], key=lambda (a, b, c): b, reverse=True):
                if type(v) == float:
                    logger.debug("\t%s: %8f" % (formatTimestamp(t), v))
                else:
                    logger.debug("\t%s: %s" % (formatTimestamp(t), v))

    def loadFromFile(self, filename):
        """
        Load values from a scenario file.
        :param filename: Absolute or relative filepath of scenario file
        """
        with open(filename, "r") as f:
            i = 1
            for line in f:
                line = line.strip()
                if line:
                    if not line.startswith("#"):
                        tmp = line.split(" ")
                        eventType = tmp[0]
                        if eventType == "OPTION":
                            optionType = tmp[1]
                            if optionType == "description":
                                self.description = line[len("OPTION description "):]
                            elif optionType == "name":
                                self.name = line[len("OPTION name "):]
                        elif eventType == "MEASUREMENT":
                            valueType = tmp[1]
                            key = tmp[2]
                            value = tmp[3]
                            if valueType == "B":
                                assert value == "True" or value == "False"
                                value = True if value == "True" else False
                            elif valueType == "F":
                                value = float(value)
                            else:
                                logger.error("Line %d: Unknown valueType: %s" % (i, valueType))
                                assert False
                            self.updateValue(key, value)
                        elif eventType == "COMMAND":
                            pass
                        elif eventType == "WAIT":
                            pass
                        elif eventType == "C102":
                            pass
                        else:
                            logger.error("Line %d: Unknown eventType: %s" % (i, eventType))
                            assert False
                i += 1


def saveValuesToFile(valueStoreObject, autosave=False):
    """
    Save the ValueStore to a file.
    :param valueStoreObject: ValueStore that should be saved
    :param autosave: True if this is an autosave
    """
    if not os.path.exists(DUMP_PATH):
        os.makedirs(DUMP_PATH)
    if autosave:
        with open(DUMP_PATH + AUTOSAVE_FILENAME, 'wb') as f:
            pickle.dump(valueStoreObject, f, pickle.HIGHEST_PROTOCOL)
    else:
        with open(DUMP_PATH + LAST_DUMP_FILENAME, 'wb') as f:
            pickle.dump(valueStoreObject, f, pickle.HIGHEST_PROTOCOL)
        with open(DUMP_PATH + ("valueStoreDump_%s.json" % formatTimestamp(time.time(), fileFormat=True)), 'wb') as f:
            json.dump(valueStoreObject.store, f, pickle.HIGHEST_PROTOCOL)
        with open(DUMP_PATH + ("valueHistoryDump_%s.json" % formatTimestamp(time.time(), fileFormat=True)), 'wb') as f:
            json.dump(valueStoreObject.history, f, pickle.HIGHEST_PROTOCOL)


def loadValuesFromFile(loadAutosave=False):
    """
    Load a ValueStore from the last dump file.
    :param: loadAutosave: True if the last autosave should be loaded
    :return: Loaded ValueStore
    """
    if loadAutosave:
        return pickle.load(open(DUMP_PATH + AUTOSAVE_FILENAME))
    else:
        return pickle.load(open(DUMP_PATH + LAST_DUMP_FILENAME))


if __name__ == '__main__':
    # Tests
    initializeLogging(level=logging.INFO, logLevel=False, logLocation=False, logTime=True)
    To = ValueStore("Tobserved")
    To.updateValue("V1", 1.0)
    assert To.retrieveValue("V1") == 1
    To.updateValue("V2", 2.5)
    To.updateValue("V1", 666)
    time.sleep(1)
    To.updateValue("V1", -1)
    To.updateValue("V1", 6.222323)
    To.updateValue("V1", 6)
    To.updateValue("A2", 4.2)
    To.updateValue("Test", 6.66)
    time.sleep(1)
    To.updateValue("V1", 2)
    To.updateValue("V1", 4)
    To.updateValue("V2", 5)
    assert To.retrieveValue("V1") == 4
    assert To.retrieveValueBefore("V1", time.time() - 1.5) == 666
    try:
        v = To.retrieveValueBefore("V1", time.time() - 10)
        print v
        assert False
    except ValueNotStoredException, e:
        assert True
    assert To.retrieveValue("V2") == 5
    To.printCurrentState()
    To.printHistory("V1")
    To.printFullHistory()
    To.updateValue("V1", 1)
    Tc = To.getCopy(newName="Tcalculated")
    Tc.updateValue("V1", 2)
    Tc.invalidateValue("V1")
    assert To.retrieveValue("V1") == 1
    try:
        Tc.retrieveValue("V1")
        assert False
    except ValueNotStoredException, e:
        assert True
    assert Tc.retrieveValue("V1", True) == 2
    To.updateValue("N1", 1)
    To.updateValue("N2", 2)
    Tc.updateValue("M1", 3)
    Tc.updateValue("M2", 4)
    Tc.compareTo(To)
