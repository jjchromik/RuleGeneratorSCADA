#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This class represents a power line.
'''
from GridComponents.AbstractComponent import AbstractComponent
from GridComponents.Fuse import Fuse
from GridComponents.Meter import Meter
from GridComponents.ProtectiveRelay import ProtectiveRelay
from GridComponents.Switch import Switch


class PowerLine(AbstractComponent):
    def __init__(self, name, maxI, nominalV=230, startSwitch=None, endSwitch=None, startMeter=None, endMeter=None,
                 startFuse=None, endFuse=None, startProtectiveRelay=None, endProtectiveRelay=None, voltageBoundaryFactor=0.10):
        """
        Initialize a power line.
        :param name: Name of the power line.
        :param maxI: Current safety threshold for physical cable
        :param nominalV: Nominal voltage
        :param startSwitch: Switch at start of line (if any)
        :param endSwitch: Switch at end of line (if any)
        :param startMeter: Meter at start of line (if any)
        :param endMeter: Meter at end of line (if any)
        :param startFuse: Fuse at start of line (if any)
        :param endFuse: Fuse at end of line (if any)
        :param startProtectiveRelay: Protective relay at start of line (if any)
        :param endProtectiveRelay: Protective relay at end of line (if any)
        :param voltageBoundaryFactor: Allowed deviation from nominal voltage in both directions
        """
        super(PowerLine, self).__init__(name)
        assert maxI
        assert nominalV
        assert not startSwitch or isinstance(startSwitch, Switch)
        assert not endSwitch or isinstance(endSwitch, Switch)
        assert not startMeter or isinstance(startMeter, Meter)
        assert not endMeter or isinstance(endMeter, Meter)
        assert not startFuse or isinstance(startFuse, Fuse)
        assert not endFuse or isinstance(endFuse, Fuse)
        assert not startProtectiveRelay or isinstance(startProtectiveRelay, ProtectiveRelay)
        assert not endProtectiveRelay or isinstance(endProtectiveRelay, ProtectiveRelay)
        self.maxI = maxI
        self.nominalV = nominalV
        self.voltageBoundaryFactor = voltageBoundaryFactor
        self.startMeter = startMeter if startMeter else Meter("%s_START_METER" % self.name.upper())
        self.startMeter.setLine(self)
        self.endMeter = endMeter if endMeter else Meter("%s_END_METER" % self.name.upper())
        self.endMeter.setLine(self)
        self.startSwitch = startSwitch if startSwitch else Switch("%s_START_SWITCH" % self.name.upper())
        self.startSwitch.setLine(self)
        self.endSwitch = endSwitch if endSwitch else Switch("%s_END_SWITCH" % self.name.upper())
        self.endSwitch.setLine(self)
        self.startFuse = startFuse
        if startFuse:
            self.startFuse.setLine(self)
        self.endFuse = endFuse
        if endFuse:
            self.endFuse.setLine(self)
        self.startProtectiveRelay = startProtectiveRelay
        if startProtectiveRelay:
            self.startProtectiveRelay.setLine(self)
        self.endProtectiveRelay = endProtectiveRelay
        if endProtectiveRelay:
            self.endProtectiveRelay.setLine(self)

    def setStartNode(self, startNode):
        """
        Set the start node for this line.
        :param startNode: Desired start node
        """
        assert startNode
        self.startNode = startNode
        self.startMeter.connectedNode = startNode
        self.startSwitch.connectedNode = startNode
        if self.startFuse:
            self.startFuse.connectedNode = startNode
        if self.startProtectiveRelay:
            self.startProtectiveRelay.connectedNode = startNode

    def setEndNode(self, endNode):
        """
        Set the end node for this line.
        :param endNode: Desired end node
        """
        assert endNode
        self.endNode = endNode
        self.endMeter.connectedNode = endNode
        self.endSwitch.connectedNode = endNode
        if self.endFuse:
            self.endFuse.connectedNode = endNode
        if self.endProtectiveRelay:
            self.endProtectiveRelay.connectedNode = endNode

    def getLocalComponent(self, connectedNode, location, type):
        """
        Return a component in relation to a given node.
        :param connectedNode: Either start or end node of this power line
        :param location: "local" or "remote"
        :param type: "fuse" or "protectiveRelay" or "switch" or "meter"
        :return: Component of given type which is at location relative to connectedNode
        """
        if self.startNode and self.endNode:
            assert self.startNode == connectedNode or self.endNode == connectedNode
        elif self.startNode:
            assert self.startNode == connectedNode
        else:
            assert self.endNode == connectedNode
        assert location in ["local", "remote"]
        assert type in ["fuse", "protectiveRelay", "switch", "meter"]
        if location == "local" and connectedNode == self.startNode or location == "remote" and connectedNode == self.endNode:
            if type == "fuse":
                return self.startFuse
            if type == "protectiveRelay":
                return self.startProtectiveRelay
            if type == "switch":
                return self.startSwitch
            if type == "meter":
                return self.startMeter
        if location == "local" and connectedNode == self.endNode or location == "remote" and connectedNode == self.startNode:
            if type == "fuse":
                return self.endFuse
            if type == "protectiveRelay":
                return self.endProtectiveRelay
            if type == "switch":
                return self.endSwitch
            if type == "meter":
                return self.endMeter
        assert False

    def retrieveValue(self, state, connectedNode, location, type):
        """
        Return a components value from the state in relation to a given node.
        :param state: State object
        :param connectedNode: Either start or end node of this power line
        :param location: "local" or "remote"
        :param type: "voltage" or "current" or "setPointV" or "setPointI", "switchState" or "fuseState" or "protectiveRelayState"
        :return: Value of desired type which is at location relative to connectedNode
        """
        assert state
        if self.startNode and self.endNode:
            assert self.startNode == connectedNode or self.endNode == connectedNode
        elif self.startNode:
            assert self.startNode == connectedNode
        else:
            assert self.endNode == connectedNode
        assert location in ["local", "remote"]
        assert type in ["voltage", "current", "setPointV", "setPointI", "switchState", "fuseState",
                        "protectiveRelayState"]
        if location == "local" and connectedNode == self.startNode or location == "remote" and connectedNode == self.endNode:
            if type == "voltage":
                key = self.startMeter.voltageKey
            if type == "current":
                key = self.startMeter.currentKey
            if type == "setPointV":
                key = self.startMeter.setPointVKey
            if type == "setPointI":
                key = self.startMeter.setPointIKey
            if type == "switchState":
                key = self.startSwitch.stateKey
            if type == "fuseState":
                key = self.startFuse.stateKey
            if type == "protectiveRelayState":
                key = self.startProtectiveRelay.stateKey
        if location == "local" and connectedNode == self.endNode or location == "remote" and connectedNode == self.startNode:
            if type == "voltage":
                key = self.endMeter.voltageKey
            if type == "current":
                key = self.endMeter.currentKey
            if type == "setPointV":
                key = self.endMeter.setPointVKey
            if type == "setPointI":
                key = self.endMeter.setPointIKey
            if type == "switchState":
                key = self.endSwitch.stateKey
            if type == "fuseState":
                key = self.endFuse.stateKey
            if type == "protectiveRelayState":
                key = self.endProtectiveRelay.stateKey
        assert key
        return state.retrieveValue(key)

    def turnFlowAround(self):
        """Turn the direction of current flow of this line around. Adjust nodes too"""
        from Bus import Bus
        assert isinstance(self.endNode, Bus) and isinstance(self.startNode, Bus)
        self.endNode.linesIn.remove(self)
        self.endNode.linesOut.append(self)
        self.startNode.linesOut.remove(self)
        self.startNode.linesIn.append(self)
        tmpEndNode = self.endNode
        self.endNode = self.startNode
        self.startNode = tmpEndNode
        tmpEndMeter = self.endMeter
        self.endMeter = self.startMeter
        self.startMeter = tmpEndMeter
        tmpEndSwitch = self.endSwitch
        self.endSwitch = self.startSwitch
        self.startSwitch = tmpEndSwitch
        tmpEndFuse = self.endFuse
        self.endFuse = self.startFuse
        self.startFuse = tmpEndFuse
        tmpEndProtectiveRelay = self.endProtectiveRelay
        self.endProtectiveRelay = self.startProtectiveRelay
        self.startProtectiveRelay = tmpEndProtectiveRelay
