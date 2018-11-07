# This Bro script is a broccoli interface to a python binding
# 1) Consumer this script with bro until fully loaded
# 2) When bro script has been fully loaded, run python BroccoliInterface.py
# 3) Replay pcap file with tcpreplay

@load base/protocols/conn
@load frameworks/communication/listen
@load T104_DataTypes
@load T104_UtilityFunctions
@load T104_PhysicalTags_Masterthesis

module T104_Broccoli;

export{
	redef T104_UtilityFunctions::DEBUG_LEVEL=2;
	const RTU_NUMBER = 1001;
}

# Start a bro listening service and add local device as node. Register events for node.
redef Communication::listen_port = 47758/tcp;
redef Communication::nodes += {
	["python_t104_broccoli_interface"] = [$host = 127.0.0.1, $events = /returnPoint/, $connect=F, $ssl=F]
};

# Define python event
#global receiveIOARawNormalizedValue: event(loggedNetworkTime:time,currentRTU:int,currentIOA:int,rawValue:double);
#global receiveIOARawDoubleValue: event(loggedNetworkTime:time,currentRTU:int,currentIOA:int,rawValue:double);
#global receiveTagValue : event(loggedNetworkTime:time, tagName:string, measuredValue:double);
global receiveTagRawValue: event(loggedNetworkTime:time,tagName:string,context:string,rawValue:double,rawType:string);
global receiveTagSinglePoint: event(loggedNetworkTime:time,tagName:string,context:string,singlePoint:bool);



event bro_init(){
	Communication::connect_peer("python_t104_broccoli_interface");
}

# Functioncode 09: m_me_na_1 (Normalized Value)
event t104::m_me_na_1(c: connection, measured: T104_DataTypes::ioa_raw_value_pair_t) {
	local rtuNumber = RTU_NUMBER;
	local address = measured$address;
	local nvalue = T104_UtilityFunctions::normalize_value(measured$value);
	local value = T104_UtilityFunctions::denormalize_value(nvalue,T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address]$normalizationInterval);
	local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];

	event receiveTagRawValue(network_time(), current_physical_tag$tagName, "measured", value, "real");
}

# Functioncode 21: m_me_nd_1 (Normalized Value)
event t104::m_me_nd_1(c: connection, measured: T104_DataTypes::ioa_raw_value_pair_t) {	
	local rtuNumber = RTU_NUMBER;
	local address = measured$address;
	local nvalue = T104_UtilityFunctions::normalize_value(measured$value);
	local value = T104_UtilityFunctions::denormalize_value(nvalue,T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address]$normalizationInterval);
	local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];

	event receiveTagRawValue(network_time(), current_physical_tag$tagName, "measured", value, "real");
}

# Functioncode 34: m_me_td_1 (Normalized Value)
event t104::m_me_td_1(c: connection, measured: T104_DataTypes::ioa_raw_value_pair_t) { 
	local rtuNumber = RTU_NUMBER;
	local address = measured$address;
	local nvalue = T104_UtilityFunctions::normalize_value(measured$value);
	local value = T104_UtilityFunctions::denormalize_value(nvalue,T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address]$normalizationInterval);
	local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];

	event receiveTagRawValue(network_time(), current_physical_tag$tagName, "measured", value, "real");
}

# Functioncode 13: m_me_nc_1 (Float Value)
event t104::m_me_nc_1(c: connection, measured: T104_DataTypes::ioa_raw_value_pair_t) { 
	local rtuNumber = RTU_NUMBER;
	local address = measured$address;
	local value = measured$value;
	local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];

	event receiveTagRawValue(network_time(), current_physical_tag$tagName, "measured", value, "double");
}

# Functioncode 36: m_me_tf_1 (Float Value)
event t104::m_me_tf_1(c: connection, measured: T104_DataTypes::ioa_raw_value_pair_t) {
	local rtuNumber = RTU_NUMBER;
	local address = measured$address;
	local value = measured$value;
	local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];

	event receiveTagRawValue(network_time(), current_physical_tag$tagName, "measured", value, "double");
}

# Functioncode 03: m_dp_na_1 (Double Point Value)
event t104::m_dp_na_1(c: connection, measured: T104_DataTypes::ioa_raw_value_pair_t) { 
	local rtuNumber = RTU_NUMBER;
	local address = measured$address;
	local value = measured$value;
	local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];

	event receiveTagRawValue(network_time(), current_physical_tag$tagName, "measured", value, "doublePoint");
}

# Functioncode 31: m_dp_tb_1 (Double Point Value)
event t104::m_dp_tb_1(c: connection, measured: T104_DataTypes::ioa_raw_value_pair_t) { 
	local rtuNumber = RTU_NUMBER;
	local address = measured$address;
	local value = measured$value;
	local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];

	event receiveTagRawValue(network_time(), current_physical_tag$tagName, "measured", value, "doublePoint");
}

# Functioncode 01: m_sp_na_1 (Bool Value)
event t104::m_sp_na_1(c: connection, measured: T104_DataTypes::ioa_single_point_value_pair_t){
	local rtuNumber = RTU_NUMBER;
	local address = measured$address;
	local value = measured$value;
	local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];

	event receiveTagSinglePoint(network_time(), current_physical_tag$tagName, "measured", value);
}

# Functioncode 30: m_sp_tb_1 (Bool Value)
event t104::m_sp_tb_1(c: connection, measured: T104_DataTypes::ioa_single_point_value_pair_t){
	local rtuNumber = RTU_NUMBER;
	local address = measured$address;
	local value = measured$value;
	local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];

	event receiveTagSinglePoint(network_time(), current_physical_tag$tagName, "measured", value);
}

# Functioncode 48: c_se_na_1 (Normalized Value)
event t104::c_se_na_1(c: connection, commanded: T104_DataTypes::ioa_raw_value_pair_t) {
	local rtuNumber = RTU_NUMBER;
	local address = commanded$address;
	local nvalue = T104_UtilityFunctions::normalize_value(commanded$value);
	local value = T104_UtilityFunctions::denormalize_value(nvalue,T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address]$normalizationInterval);
	local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];

	event receiveTagRawValue(network_time(), current_physical_tag$tagName, "commanded", value, "real");
}

# Functioncode 61: c_se_ta_1 (Normalized Value)
event t104::c_se_ta_1(c: connection, commanded: T104_DataTypes::ioa_raw_value_pair_t) {
	local rtuNumber = RTU_NUMBER;
	local address = commanded$address;
	local nvalue = T104_UtilityFunctions::normalize_value(commanded$value);
	local value = T104_UtilityFunctions::denormalize_value(nvalue,T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address]$normalizationInterval);
	local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];

	event receiveTagRawValue(network_time(), current_physical_tag$tagName, "commanded", value, "real");
}

# Functioncode 50: c_se_nc_1 (Float Value)
event t104::c_se_nc_1(c: connection, commanded: T104_DataTypes::ioa_raw_value_pair_t) {
	local rtuNumber = RTU_NUMBER;
	local address = commanded$address;
	local value = commanded$value;
	local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];

	event receiveTagRawValue(network_time(), current_physical_tag$tagName, "commanded", value, "double");
}

# Functioncode 63: c_se_tc_1 (Float Value)
event t104::c_se_tc_1(c: connection, commanded: T104_DataTypes::ioa_raw_value_pair_t) {
	local rtuNumber = RTU_NUMBER;
	local address = commanded$address;
	local value = commanded$value;
	local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];

	event receiveTagRawValue(network_time(), current_physical_tag$tagName, "commanded", value, "double");
}

# Functioncode 46: c_dc_na_1 (Double Point Value)
event t104::c_dc_na_1(c: connection, commanded: T104_DataTypes::ioa_raw_value_pair_t) {
	local rtuNumber = RTU_NUMBER;
	local address = commanded$address;
	local value = commanded$value;
	local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];

	event receiveTagRawValue(network_time(), current_physical_tag$tagName, "commanded", value, "doublePoint");
}

# Functioncode 59: c_dc_ta_1 (Double Point Value)
event t104::c_dc_ta_1(c: connection, commanded: T104_DataTypes::ioa_raw_value_pair_t) {
	local rtuNumber = RTU_NUMBER;
	local address = commanded$address;
	local value = commanded$value;
	local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];

	event receiveTagRawValue(network_time(), current_physical_tag$tagName, "commanded", value, "doublePoint");
}

# Functioncode 45: c_sc_na_1 (Bool Value)
event t104::c_sc_na_1(c: connection, commanded: T104_DataTypes::ioa_single_point_value_pair_t){
	local rtuNumber = RTU_NUMBER;
	local address = commanded$address;
	local value = commanded$value;
	local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];

	event receiveTagSinglePoint(network_time(), current_physical_tag$tagName, "commanded", value);
}

# Functioncode 58: c_sc_ta_1 (Bool Value)
event t104::c_sc_ta_1(c: connection, commanded: T104_DataTypes::ioa_single_point_value_pair_t){
	local rtuNumber = RTU_NUMBER;
	local address = commanded$address;
	local value = commanded$value;
	local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];

	event receiveTagSinglePoint(network_time(), current_physical_tag$tagName, "commanded", value);
}

# Return event
event returnPoint(note:string)
{
	T104_UtilityFunctions::print_debug(fmt("[Bro] [Python return event] %s",note),2);
}

