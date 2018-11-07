#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This abstract class is parent class of every decorator component of the electrical grid model (meter, switch, fuse, protective relay).
'''
from GridComponents.AbstractComponent import AbstractComponent


class AbstractDecorator(AbstractComponent):
    def __init__(self, name):
        """
        Initialize a decorator type.
        :param name: Name of the decorator.
        """
        super(AbstractDecorator, self).__init__(name)

    def setLine(self, connectedLine):
        """
        Set the connected line for this decorator.
        :param connectedLine: Line this decorator is attached to
        """
        self.connectedLine = connectedLine

    def setNode(self, connectedNode):
        """
        Set the connected node for this decorator.
        :param connectedNode: Node with line this decorator is attached to
        """
        self.connectedNode = connectedNode
