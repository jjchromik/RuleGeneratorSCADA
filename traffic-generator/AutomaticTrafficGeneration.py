#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This traffic generator automatically generated pcapng traffic dumps from scenarios.

IMPORTANT:
Put this line into /etc/sudoers (via sudo visudo):
username ALL=(ALL) NOPASSWD:/usr/sbin/tcpdump
'''
import Queue
import os
import pexpect
import threading
from time import sleep

import pyshark

from GenerateScenarioTrafficExtended import connectToServer, sendData
from Server import initializeServer, listenForData


def captureTrafficPyshark(name, caseName, caseNumber, normalized, captureReady):
    """
    Capture the iec-104 traffic on lo into a file.
    :param name: Name of thread
    :param caseName: Scenario case
    :param caseNumber: Scenario number of case
    :param normalized: normalized (True) or float (False) values
    :param captureReady: Signal for capturing is ready (sending)
    """
    if normalized:
        pcapFilename = "/tmp/traffic/%s_Normalized_Scenario%d.pcapng" % (caseName, caseNumber)
    else:
        pcapFilename = "/tmp/traffic/%s_Scenario%d.pcapng" % (caseName, caseNumber)
    capture = pyshark.LiveCapture("lo", bpf_filter="port 2404 ", output_file=pcapFilename)
    captureReady.put(True)
    capture.sniff(timeout=20)
    print capture


def captureTrafficTcpdump(name, caseName, caseNumber, normalized, captureReady, sendingFinished):
    """
    Capture the iec-104 traffic on lo into a file.
    :param name: Name of thread
    :param caseName: Scenario case
    :param caseNumber: Scenario number of case
    :param normalized: normalized (True) or float (False) values
    :param captureReady: Signal for capturing is ready (sending)
    :param sendingFinished: Signal for sending of data is finished (receiving)
    """
    if normalized:
        pcapFilename = "/tmp/traffic/%s_Normalized_Scenario%d.pcapng" % (caseName, caseNumber)
    else:
        pcapFilename = "/tmp/traffic/%s_Scenario%d.pcapng" % (caseName, caseNumber)
    command = "sudo /usr/sbin/tcpdump -i lo port 2404 -w %s" % pcapFilename
    process = pexpect.spawn(command)
    captureReady.put(True)
    sendingFinished.get()
    sleep(1)
    process.sendcontrol("c")


def createServer(name, captureReady, serverReady):
    """
    Start the server which receives iec-104 traffic.
    :param name: Name of thread
    :param captureReady: Signal for capturing is ready (receiving)
    :param serverReads: Signal for server is ready to receive data (sending)
    """
    captureReady.get()
    sleep(1)
    sock = initializeServer()
    serverReady.put(True)
    listenForData(sock, runOnlyOnce=True)


def sendTraffic(name, caseName, caseNumber, normalized, serverReady, sendingFinished):
    """
    Read the scenario files and send the traffic.
    :param name: Name of thread
    :param caseName: Scenario case
    :param caseNumber: Scenario number of case
    :param normalized: normalized (True) or float (False) values
    :param serverReads: Signal for server is ready to receive data (receiving)
    :param sendingFinished: Signal for sending of data is finished (sending)
    """
    serverReady.get()
    sleep(1)
    sock = connectToServer()
    sendData(sock, caseName, caseNumber, normalized)
    sendingFinished.put(True)


def startGeneration(caseName, caseNumber, normalized):
    """
    Start three threads and manage concurrency for traffic receiving, sending and capturing.
    :param caseName: Scenario case
    :param caseNumber: Scenario number of case
    :param normalized: normalized (True) or float (False) values
    """
    if not os.path.exists("/tmp/traffic"):
        os.makedirs("/tmp/traffic")
    captureReady = Queue.Queue()
    serverReady = Queue.Queue()
    sendingFinished = Queue.Queue()
    t1 = threading.Thread(target=captureTrafficTcpdump, args=("t1", caseName, caseNumber, normalized, captureReady, sendingFinished))
    t1.start()
    t2 = threading.Thread(target=createServer, args=("t2", captureReady, serverReady))
    t2.start()
    t3 = threading.Thread(target=sendTraffic, args=("t3", caseName, caseNumber, normalized, serverReady, sendingFinished))
    t3.start()
    t3.join()
    t2.join()
    t1.join()
    print "Finished with Case %s Scenario %d" % (caseName, caseNumber)


if __name__ == '__main__':
    for normalized in [True, False]:
        for i in xrange(1, 9 + 1):
            startGeneration(caseName="Masterthesis_GlobalKnowledge", caseNumber=i, normalized=normalized)
        # for i in xrange(1, 8 + 1):
        #     startGeneration(caseName="Alpha_GlobalKnowledge", caseNumber=i, normalized=normalized)
        # for i in xrange(1, 3 + 1):
        #     startGeneration(caseName="Alpha_LocalKnowledge", caseNumber=i, normalized=normalized)
