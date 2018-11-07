#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

Every class representing a physical part of the electrical grid is subclass of this abstract component.
This class ensures that every component has a name and offers a function to return all components there are.
Furthermore it can be used for type checks and constraints.
'''


class AbstractComponent(object):
    allComponents = []
    allNames = []

    def __init__(self, name):
        """
        Initialize a component with a name.
        :param name: Name of the component
        """
        assert name
        # assert name not in AbstractComponent.allNames
        self.name = name
        AbstractComponent.allComponents.append(self)
        AbstractComponent.allNames.append(name)


def getAllComponentsOfType(type):
    """
    Return all components of the given type.
    :param type: Class that represents the desired grid component
    :return: List of all components with the given type
    """
    return [c for c in AbstractComponent.allComponents if isinstance(c, type)]


def getComponentByName(name):
    """
    Return the component of the given name.
    :param name: Searched name
    :return: Components with the given name
    """
    for c in AbstractComponent.allComponents:
        if c.name == name:
            return c
    return None
