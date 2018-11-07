#!/usr/bin/python
# -*- coding: utf-8 -*-
'''


'''

BRO_SCRIPT_FILENAME_TEMPLATE = "T104_PhysicalTags_%s.bro"
BRO_FORMAT_STRING = '\t\tPHYSICAL_TAG_MAP[%s,%d]=[$name="%s", $description="%s", $tagName="%s", $dimension="%s", $normalizationInterval=[$min=%f, $max=%f]];\n'

BRO_SCRIPT_CONTENT_TRAILER = """# This Bro script is automatically generated and contains the RTU's config in PHYSICAL_TAG_MAP.
# The values are extracted from the RTU configuration.

@load T104_DataTypes

module T104_PhysicalTags;

export
{
	global PHYSICAL_TAG_MAP : T104_DataTypes::physical_tag_map_t;

	function populate_physical_tag_map()
	{
"""
BRO_SCRIPT_CONTENT_FOOTER = """  } 
}
# Initialization code
event bro_init(){
	populate_physical_tag_map();
}
"""
