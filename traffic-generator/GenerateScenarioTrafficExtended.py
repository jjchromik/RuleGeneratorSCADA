#!/usr/bin/python
# -*- coding: utf-8 -*-
'''


'''

import binascii
import datetime
import os
import socket
import time

from APDUType102 import APDUType102
from APDUType30 import APDUType30
from APDUType34 import APDUType34
from APDUType36 import APDUType36
from APDUType58 import APDUType58
from APDUType61 import APDUType61
from APDUType63 import APDUType63
from GeneratePhysicalTagMap import getTagDict
from StateManagerUtilities import isZero
from TrafficConstants import SERVER_HOST, SERVER_PORT

RTU_NUMBER = 1001
SCENARIO_PATH = "../state-manager/Scenarios/"
RTU_CONFIGURATION_FILE = "../policy-generator/rtu-configs/%s%s_RTU_Configuration.csv"


def connectToServer():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))
    return sock


def normalizeValue(value, lowerBound, upperBound):
    v = ((value - lowerBound) / (upperBound - lowerBound)) * 2.0 - 1.0
    assert -1 <= v and v <= 1
    return v


def sendValue(sock, rtuTags, eventType, k, v):
    apdu = None
    try:
        if eventType == "C102":
            apdu = APDUType102(RTU_NUMBER, rtuTags[k].addresses[1])
        else:
            if type(v) == float:
                if not isZero(rtuTags[k].lowerBound) and not isZero(rtuTags[k].lowerBound):
                    v = normalizeValue(v, rtuTags[k].lowerBound, rtuTags[k].upperBound)
                    if eventType == "COMMAND":
                        apdu = APDUType61(RTU_NUMBER, rtuTags[k].addresses[2], v, datetime.datetime.now())
                    elif eventType == "MEASUREMENT":
                        apdu = APDUType34(RTU_NUMBER, rtuTags[k].addresses[1], v, datetime.datetime.now())
                    else:
                        assert False
                else:
                    if eventType == "COMMAND":
                        apdu = APDUType63(RTU_NUMBER, rtuTags[k].addresses[2], v, datetime.datetime.now())
                    elif eventType == "MEASUREMENT":
                        apdu = APDUType36(RTU_NUMBER, rtuTags[k].addresses[1], v, datetime.datetime.now())
                    else:
                        assert False
            elif type(v) == bool:
                if eventType == "COMMAND":
                    apdu = APDUType58(RTU_NUMBER, rtuTags[k].addresses[2], v, datetime.datetime.now())
                elif eventType == "MEASUREMENT":
                    apdu = APDUType30(RTU_NUMBER, rtuTags[k].addresses[1], v, datetime.datetime.now())
                else:
                    assert False
            else:
                print "Value type not valid. (Allowed: Bool, Float)"
                assert False
    except Exception, e:
        print "Exception while creating APDUs: %s" % e.message
        assert False

    if apdu:
        print "Sending '%s'" % binascii.hexlify(apdu.toBytes())
        sock.sendall(apdu.toBytes())
        time.sleep(0.03)
    else:
        print "APDU empty?"
        assert False


def processScenarioFile(sock, scenarioFilename, caseName, normalized):
    """
    Generate traffic from a scenario file.
    :param sock: Open network socket
    :param scenarioFilename: Absolute or relative filepath of scenario file
    :param caseName: Name of case
    :param normalized: True if normalization of values desired
    """
    rtuTags = None
    try:
        if normalized:
            rtuConfigFile = RTU_CONFIGURATION_FILE % (caseName, "_Normalized")
        else:
            rtuConfigFile = RTU_CONFIGURATION_FILE % (caseName, "")
        rtuTags = getTagDict(rtuConfigFile)
    except Exception, e:
        print "RTU configuration could not be loaded. %s" % e
        assert False
    if rtuTags:
        with open(scenarioFilename, "r") as f:
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
                                pass
                            elif optionType == "name":
                                pass
                        elif eventType == "MEASUREMENT" or eventType == "COMMAND":
                            valueType = tmp[1]
                            key = tmp[2]
                            value = tmp[3]
                            if valueType == "B":
                                assert value == "True" or value == "False"
                                value = True if value == "True" else False
                            elif valueType == "F":
                                value = float(value)
                            else:
                                print "Line %d: Unknown valueType: %s" % (i, valueType)
                                assert False

                            sendValue(sock, rtuTags, eventType, key, value)
                            # send key,value measurement here
                        elif eventType == "WAIT":
                            duration = float(tmp[1])
                            time.sleep(duration)
                        elif eventType == "C102":
                            key = tmp[1]
                            sendValue(sock, rtuTags, eventType, key, 0.0)
                        else:
                            print "Line %d: Unknown eventType: %s" % (i, eventType)
                            assert False
                i += 1


def generateScenarioTraffic(sock, caseName, caseNumber, normalized):
    scenarioFiles = []
    basicCaseFilename = "%s_%s.state" % (caseName, "BasicCase")
    scenarioFilename = "%s_%s.state" % (caseName, "Scenario%d" % caseNumber)
    basicCaseFound = False
    for filename in os.listdir(SCENARIO_PATH):
        if filename == basicCaseFilename:
            basicCaseFound = True
        else:
            if filename.startswith(caseName) and filename.endswith(".state"):
                scenarioFiles.append(filename)
    assert basicCaseFound
    assert scenarioFilename in scenarioFiles

    processScenarioFile(sock, "%s%s" % (SCENARIO_PATH, basicCaseFilename), caseName, normalized)
    processScenarioFile(sock, "%s%s" % (SCENARIO_PATH, scenarioFilename), caseName, normalized)


def sendData(sock, caseName, caseNumber, normalized):
    try:
        generateScenarioTraffic(sock, caseName, caseNumber, normalized)
    finally:
        print "Closing socket"
        sock.close()


if __name__ == '__main__':
    sock = connectToServer()
    sendData(sock, caseName="Alpha_GlobalKnowledge", caseNumber=8, normalized=True)
