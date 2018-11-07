#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This script generates the Bro code for the function populate_physical_tag_map() which initializes the constant PHYSICAL_TAG_MAP.
PHYSICAL_TAG_MAP is a table (hashmap) in which each physical_tag_t is referenced by a tuple (rtu_number_t,address_t).
It is generated from the RTU configuration given in csv format.
'''

import csv

from PolicyGeneratorConstants import *

# Outside of git repository ("Workspace" is mountpoint for /data directory in docker container created from rf/broccoli-hilti)
BRO_SCRIPT_PATH = "/home/rf/Daten/Masterarbeit/iec-104/policy-generator/generated-bro-scripts/"
RTU_CONFIG_TO_GENERATE = "Alpha"
RTU_CONFIG_TO_GENERATE = "Masterthesis"

RTU_CONFIG_FILES = dict()
ALPHA_RTU_CONFIG_INPUT_FILENAME = "../policy-generator/rtu-configs/Alpha_GlobalKnowledge_Normalized_RTU_Configuration.csv"
MASTERTHESIS_RTU_CONFIG_INPUT_FILENAME = "../policy-generator/rtu-configs/Masterthesis_GlobalKnowledge_Normalized_RTU_Configuration.csv"
RTU_CONFIG_FILES["Alpha"] = [ALPHA_RTU_CONFIG_INPUT_FILENAME]
RTU_CONFIG_FILES["Masterthesis"] = [MASTERTHESIS_RTU_CONFIG_INPUT_FILENAME]


class PhysicalTag:
    def __init__(self, tagName, name, description, dimension, rtuNumber, addresses, lowerBound, upperBound):
        self.tagName = tagName
        self.name = name
        self.description = description
        self.dimension = dimension
        self.rtuNumber = rtuNumber
        self.addresses = addresses
        self.lowerBound = lowerBound
        self.upperBound = upperBound


def parseRTUConfiguration(rtuConfigurationFilenames, createBroFile=False):
    """
    Parse the RTU configuration and generate a full list of tag information for every line
    :param rtuConfigurationFilenames: Filename of RTU configuration
    :param createBroFile: True if a Bro script should be created
    :return: List of all tags and tag information (lines of RTU configuration)
    """
    broFileContent = BRO_SCRIPT_CONTENT_TRAILER
    for rtuConfig in rtuConfigurationFilenames:
        rtuTags = []
        with open(rtuConfig) as rtuConfigOutputs:
            csvData = csv.DictReader(rtuConfigOutputs, delimiter=',')
            for row in csvData:
                givenAddresses = []
                for addressType in ["Address", "IOA_M", "IOA_Mtt", "IOA_C"]:
                    if addressType in row:
                        try:
                            givenAddresses.append(int(row[addressType]))
                        except:
                            pass
                if row.has_key("LowerBound") and row["LowerBound"] and row.has_key("UpperBound") and row["UpperBound"]:
                    lowerBound = float(row["LowerBound"])
                    upperBound = float(row["UpperBound"])
                else:
                    lowerBound = 0.0
                    upperBound = 0.0
                if row.has_key("Description"):
                    description = row["Description"]
                elif row.has_key("IoDescription"):
                    description = row["IoDescription"]
                else:
                    description = ""
                dimensionText = row["DimensionText"] if row.has_key("DimensionText") else "Other"
                currentTag = PhysicalTag(row["TagName"], row["Name"], description, dimensionText, row["RtuNo"],
                                         givenAddresses, lowerBound, upperBound)
                rtuTags.append(currentTag)

        broFileContent += "\t\t#Rules generated from %s\n" % rtuConfig
        for tag in rtuTags:
            for address in tag.addresses:
                broFileContent += BRO_FORMAT_STRING % (
                    tag.rtuNumber, address, tag.name, tag.description, tag.tagName, tag.dimension, tag.lowerBound,
                    tag.upperBound)
        broFileContent += "\n"
    broFileContent += BRO_SCRIPT_CONTENT_FOOTER

    if createBroFile:
        writeBroFile(broFileContent)

    return rtuTags


def writeBroFile(broFileContent):
    """
    Write the file content to disk.
    :param broFileContent: Content of bro script
    """
    print "Writing Bro file."
    filename = BRO_SCRIPT_PATH + (BRO_SCRIPT_FILENAME_TEMPLATE % RTU_CONFIG_TO_GENERATE)
    with open(filename, "w") as broFile:
        broFile.write(broFileContent)


def getTagDict(rtuConfigurationFilename):
    """
    Generate a dictionary containing all tag information from an RTU configuration.
    :param rtuConfigurationFilename: Path to RTU configuration
    :return: Dictionary with tagName as key
    """
    rtuTags = parseRTUConfiguration([rtuConfigurationFilename], createBroFile=False)
    pythonTagDict = dict()
    for tag in rtuTags:
        pythonTagDict[tag.tagName] = tag
    return pythonTagDict


def getTagNamesToIOA(rtuConfigurationFilename):
    """
    Generate a dictionary containing info object addresses from an RTU configuration.
    :param rtuConfigurationFilename: Path to RTU configuration
    :return: Dictionary with tagName as key
    """
    rtuTags = parseRTUConfiguration([rtuConfigurationFilename], createBroFile=False)
    pythonTagDict = dict()
    for tag in rtuTags:
        pythonTagDict[tag.tagName] = tag.addresses[0]
    return pythonTagDict


if __name__ == '__main__':
    rtuTags = parseRTUConfiguration(RTU_CONFIG_FILES[RTU_CONFIG_TO_GENERATE], createBroFile=True)
    print "Finished."
