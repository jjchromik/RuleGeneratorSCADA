# This Bro script is printing all measured values of Type IDs 1, 9, 30, 34, 36

@load base/protocols/conn
@load T104_DataTypes
@load T104_UtilityFunctions
@load T104_PhysicalTags

module T104_MV_Events;

export{
	redef enum Log::ID += {LOG_measuredValues};
	redef T104_UtilityFunctions::DEBUG_LEVEL=2;
	const RTU_NUMBER = 1001;

	type value_time_t:record {
		measuredValue: T104_DataTypes::normalized_value_t;
		networkTime: time;
	};
	type single_point_time_t:record {
		measuredValue: T104_DataTypes::single_point_value_t;
		networkTime: time;
	};
	type vector_of_value_time_t : vector of value_time_t;
	type vector_of_single_point_time_t : vector of single_point_time_t;
	type vector_of_value_t : vector of T104_DataTypes::normalized_value_t;
	type vector_of_single_point_t : vector of T104_DataTypes::single_point_value_t;
	type values_over_time_t : table[T104_DataTypes::rtu_number_t,T104_DataTypes::address_t] of vector_of_value_time_t;
	type single_point_over_time_t : table[T104_DataTypes::rtu_number_t,T104_DataTypes::address_t] of vector_of_single_point_time_t;	

	global normalized_values_over_time : values_over_time_t;
	global single_point_over_time : single_point_over_time_t;
}

# Initialization code
event bro_init(){
	Log::create_stream(T104_MV_Events::LOG_measuredValues, [$columns=T104_DataTypes::log_physical_tag_entry_t, $path="measuredValues"]);
}

# Log function
function log_measured_value(c: connection, tag: T104_DataTypes::physical_tag_t, note: string){
	local logRecord : T104_DataTypes::log_physical_tag_entry_t = [$ts=network_time(),$id=c$id, $note=note, $physicalTag=tag];
	Log::write(T104_MV_Events::LOG_measuredValues, logRecord);
}

# Save measured value
function add_measured_value_statistic(c: connection, measured_normalized_tuple : T104_DataTypes::rtu_ioa_normalized_value_tuple_t) {
	local rtuNumber = measured_normalized_tuple$rtuNo;
	local address = measured_normalized_tuple$address;
	local value = measured_normalized_tuple$value;
	if ([rtuNumber,address] in T104_PhysicalTags::PHYSICAL_TAG_MAP){
		local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];
		local value_time = value_time_t($measuredValue=value,$networkTime=network_time());
		if ([rtuNumber,address] in normalized_values_over_time){
			normalized_values_over_time[rtuNumber,address][|normalized_values_over_time[rtuNumber,address]|]=value_time;
		} else {
			normalized_values_over_time[rtuNumber,address] = vector(value_time);
		}
	}
}
# Save measured single point
function add_measured_single_point_statistic(c: connection, measured_sp_tuple : T104_DataTypes::rtu_ioa_single_point_value_tuple_t) {
	local rtuNumber = measured_sp_tuple$rtuNo;
	local address = measured_sp_tuple$address;
	local value = measured_sp_tuple$value;
	if ([rtuNumber,address] in T104_PhysicalTags::PHYSICAL_TAG_MAP){
		local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];
		local sp_time = single_point_time_t($measuredValue=value,$networkTime=network_time());
		if ([rtuNumber,address] in single_point_over_time){
			single_point_over_time[rtuNumber,address][|single_point_over_time[rtuNumber,address]|]=sp_time;
		} else {
			single_point_over_time[rtuNumber,address] = vector(sp_time);
		}
	}
}

# Prints changes of measured values / single points with network time
function print_statistics_with_timestamps(){
	local note = "Values over time:";
	T104_UtilityFunctions::print_debug(note,2);
	for ([rtuNumber,address] in normalized_values_over_time){
		local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];
		note=fmt("Values for: %s",T104_UtilityFunctions::get_physical_tag_note(rtuNumber, address,current_physical_tag));
		T104_UtilityFunctions::print_debug(note,2);
		for (index in normalized_values_over_time[rtuNumber,address]){
			local value_time = normalized_values_over_time[rtuNumber,address][index];
			note=fmt("[%s]: %f",T104_UtilityFunctions::format_timestamp(value_time$networkTime),value_time$measuredValue);
			T104_UtilityFunctions::print_debug(note,2);
		}
	}
	for ([rtuNumber,address] in single_point_over_time){
		current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];
		note=fmt("Single Point for: %s",T104_UtilityFunctions::get_physical_tag_note(rtuNumber, address,current_physical_tag));
		T104_UtilityFunctions::print_debug(note,2);
		for (index in single_point_over_time[rtuNumber,address]){
			local sp_time = single_point_over_time[rtuNumber,address][index];
			note=fmt("[%s]: %s",T104_UtilityFunctions::format_timestamp(sp_time$networkTime),sp_time$measuredValue);
			T104_UtilityFunctions::print_debug(note,2);
		}
	}
}

# Prints changes of measured values / single points as vector
function print_statistics_without_timestamps(){
	local note = "Values over time:";
	T104_UtilityFunctions::print_debug(note,2);
	for ([rtuNumber,address] in normalized_values_over_time){
		local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];
		local vectorOfValue : vector_of_value_t = vector();
		for (index in normalized_values_over_time[rtuNumber,address]){
			vectorOfValue[|vectorOfValue|]=normalized_values_over_time[rtuNumber,address][index]$measuredValue;
		}
		note=fmt("Values for %s: %s",current_physical_tag$name, vectorOfValue);
		T104_UtilityFunctions::print_debug(note,2);
	}
	for ([rtuNumber,address] in single_point_over_time){
		current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];
		local vectorOfSinglePoints : vector_of_single_point_t = vector();
		for (index in single_point_over_time[rtuNumber,address]){
			vectorOfSinglePoints[|vectorOfSinglePoints|]=single_point_over_time[rtuNumber,address][index]$measuredValue;
		}
		note=fmt("Single Point for %s: %s",current_physical_tag$name, vectorOfSinglePoints);
		T104_UtilityFunctions::print_debug(note,2);
	}
}

# Print measured value
function print_measured_value(c: connection, measured_normalized_tuple : T104_DataTypes::rtu_ioa_normalized_value_tuple_t) {
	local rtuNumber = measured_normalized_tuple$rtuNo;
	local address = measured_normalized_tuple$address;
	local value = measured_normalized_tuple$value;
	if ([rtuNumber,address] in T104_PhysicalTags::PHYSICAL_TAG_MAP){
		local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];
		local note = fmt("Measured Value! Value: %f (%s)",value,T104_UtilityFunctions::get_physical_tag_note(rtuNumber, address,current_physical_tag));
		T104_UtilityFunctions::print_debug(note,2);
		log_measured_value(c,current_physical_tag,note);
	}else {
		T104_UtilityFunctions::print_debug(fmt("RTU %6d, IOA %6d not found in PHYSICAL_TAG_MAP. Value=%f",rtuNumber,address,value),2);
	}
}

# Print measured single point
function print_measured_single_point(c: connection, measured_sp_tuple : T104_DataTypes::rtu_ioa_single_point_value_tuple_t) {
	local rtuNumber = measured_sp_tuple$rtuNo;
	local address = measured_sp_tuple$address;
	local value = measured_sp_tuple$value;
	if ([rtuNumber,address] in T104_PhysicalTags::PHYSICAL_TAG_MAP){
		local current_physical_tag = T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address];
		local note = fmt("Measured Single Point! Value: %s (%s)",value,T104_UtilityFunctions::get_physical_tag_note(rtuNumber, address,current_physical_tag));
		T104_UtilityFunctions::print_debug(note,2);
		log_measured_value(c,current_physical_tag,note);
	}else {
		T104_UtilityFunctions::print_debug(fmt("RTU %6d, IOA %6d not found in PHYSICAL_TAG_MAP. Value=%f",rtuNumber,address,value),2);
	}
}

# Functioncode 09: m_me_na_1 (Normalized Value)
event t104::m_me_na_1(c: connection, measured: T104_DataTypes::ioa_raw_value_pair_t) {
	local rtuNumber = RTU_NUMBER;
	local address = measured$address;
	local nvalue = T104_UtilityFunctions::normalize_value(measured$value);
	local value = T104_UtilityFunctions::denormalize_value(nvalue,T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address]$normalizationInterval);
	local measured_normalized_tuple : T104_DataTypes::rtu_ioa_normalized_value_tuple_t = [$rtuNo=rtuNumber,$address=address,$value=value];
	print_measured_value(c,measured_normalized_tuple);
	add_measured_value_statistic(c,measured_normalized_tuple);
}

# Functioncode 21: m_me_nd_1 (Normalized Value)
event t104::m_me_nd_1(c: connection, measured: T104_DataTypes::ioa_raw_value_pair_t) {
	local rtuNumber = RTU_NUMBER;
	local address = measured$address;
	local nvalue = T104_UtilityFunctions::normalize_value(measured$value);
	local value = T104_UtilityFunctions::denormalize_value(nvalue,T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address]$normalizationInterval);
	local measured_normalized_tuple : T104_DataTypes::rtu_ioa_normalized_value_tuple_t = [$rtuNo=rtuNumber,$address=address,$value=value];
	print_measured_value(c,measured_normalized_tuple);
	add_measured_value_statistic(c,measured_normalized_tuple);
}

# Functioncode 34: m_me_td_1 (Normalized Value)
event t104::m_me_td_1(c: connection, measured: T104_DataTypes::ioa_raw_value_pair_t) { 
	local rtuNumber = RTU_NUMBER;
	local address = measured$address;
	local nvalue = T104_UtilityFunctions::normalize_value(measured$value);
	local value = T104_UtilityFunctions::denormalize_value(nvalue,T104_PhysicalTags::PHYSICAL_TAG_MAP[rtuNumber,address]$normalizationInterval);
	local measured_normalized_tuple : T104_DataTypes::rtu_ioa_normalized_value_tuple_t = [$rtuNo=rtuNumber,$address=address,$value=value];
	print_measured_value(c,measured_normalized_tuple);
	add_measured_value_statistic(c,measured_normalized_tuple);
}

# Functioncode 13: m_me_nc_1 (Float Value)
event t104::m_me_nc_1(c: connection, measured: T104_DataTypes::ioa_raw_value_pair_t) { 
	local rtuNumber = RTU_NUMBER;
	local address = measured$address;
	local value = T104_UtilityFunctions::doublefy_value(measured$value);
	local measured_normalized_tuple : T104_DataTypes::rtu_ioa_normalized_value_tuple_t = [$rtuNo=rtuNumber,$address=address,$value=value];
	print_measured_value(c,measured_normalized_tuple);
	add_measured_value_statistic(c,measured_normalized_tuple);
}

# Functioncode 36: m_me_tf_1 (Float Value)
event t104::m_me_tf_1(c: connection, measured: T104_DataTypes::ioa_raw_value_pair_t) { 
	local rtuNumber = RTU_NUMBER;
	local address = measured$address;
	local value = T104_UtilityFunctions::doublefy_value(measured$value);
	local measured_normalized_tuple : T104_DataTypes::rtu_ioa_normalized_value_tuple_t = [$rtuNo=rtuNumber,$address=address,$value=value];
	print_measured_value(c,measured_normalized_tuple);
	add_measured_value_statistic(c,measured_normalized_tuple);
}

# Functioncode 03: m_dp_na_1 (Double Point Value)
event t104::m_dp_na_1(c: connection, measured: T104_DataTypes::ioa_raw_value_pair_t) { 
	local rtuNumber = RTU_NUMBER;
	local address = measured$address;
	local value = T104_UtilityFunctions::normalize_value(measured$value);
	local measured_normalized_tuple : T104_DataTypes::rtu_ioa_normalized_value_tuple_t = [$rtuNo=rtuNumber,$address=address,$value=value];
	print_measured_value(c,measured_normalized_tuple);
	add_measured_value_statistic(c,measured_normalized_tuple);
}

# Functioncode 31: m_dp_tb_1 (Double Point Value)
event t104::m_dp_tb_1(c: connection, measured: T104_DataTypes::ioa_raw_value_pair_t) { 
	local rtuNumber = RTU_NUMBER;
	local address = measured$address;
	local value = T104_UtilityFunctions::normalize_value(measured$value);
	local measured_normalized_tuple : T104_DataTypes::rtu_ioa_normalized_value_tuple_t = [$rtuNo=rtuNumber,$address=address,$value=value];
	print_measured_value(c,measured_normalized_tuple);
	add_measured_value_statistic(c,measured_normalized_tuple);
}

# Functioncode 01: m_sp_na_1 (Bool Value)
event t104::m_sp_na_1(c: connection, measured: T104_DataTypes::ioa_single_point_value_pair_t){
	local rtuNumber = RTU_NUMBER;
	local address = measured$address;
	local value = measured$value;
	local measured_sp_tuple : T104_DataTypes::rtu_ioa_single_point_value_tuple_t = [$rtuNo=rtuNumber,$address=address,$value=value];
	print_measured_single_point(c,measured_sp_tuple);
	add_measured_single_point_statistic(c,measured_sp_tuple);
}

# Functioncode 30: m_sp_tb_1 (Bool Value)
event t104::m_sp_tb_1(c: connection, measured: T104_DataTypes::ioa_single_point_value_pair_t){
	local rtuNumber = RTU_NUMBER;
	local address = measured$address;
	local value = measured$value;
	local measured_sp_tuple : T104_DataTypes::rtu_ioa_single_point_value_tuple_t = [$rtuNo=rtuNumber,$address=address,$value=value];
	print_measured_single_point(c,measured_sp_tuple);
	add_measured_single_point_statistic(c,measured_sp_tuple);
}

# Execute after parsing whole traffic dump
event bro_done(){
	print_statistics_with_timestamps();
	print_statistics_without_timestamps();
}