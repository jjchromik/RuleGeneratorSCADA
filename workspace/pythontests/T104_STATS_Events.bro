# This Bro script is printing used iec-104 function codes in realtime and a summary afterwards.

@load base/protocols/conn
@load T104_DataTypes
@load T104_UtilityFunctions
@load T104_PhysicalTags

module T104_STATS_Events;

export{
	redef enum Log::ID += {LOG_stats};
	redef T104_UtilityFunctions::DEBUG_LEVEL=2;
	const RTU_NUMBER = 1001;
	
	type function_id_counter_t : table[count] of count;
	global functionIdCounter : function_id_counter_t;

	type info_obj_code_lookup_t : table[count] of string;
	global infoObjCodeLookup : info_obj_code_lookup_t;
}

# Initialization code
event bro_init(){
	#Log::create_stream(T104_STATS_Events::LOG_stats, [$columns=T104_DataTypes::log_physical_tag_entry_t, $path="stats"]);
}

# Prints information about ASDU
function print_asdu_details(c: connection, rtuNumber:int, infoObjectType: T104::Info_obj_code){
	local note = fmt("[%s] ASDU! RTU %d (%s:%s -> %s:%s)",T104_UtilityFunctions::format_timestamp(network_time()),rtuNumber,c$id$orig_h,c$id$orig_p,c$id$resp_h,c$id$resp_p);
	note = note + fmt(": Function ID: %s (%d)",infoObjectType,infoObjectType);
  T104_UtilityFunctions::print_debug(note,2);
}

# Adds information of current ASDU to statistics
function add_statistics(c: connection, rtuNumber:int, infoObjectType: T104::Info_obj_code){
	local functionId = int_to_count(enum_to_int(infoObjectType));
	infoObjCodeLookup[functionId] = fmt("%s",infoObjectType);
	if(functionId in functionIdCounter){
		functionIdCounter[functionId]=functionIdCounter[functionId]+1;
	}
	else {
		functionIdCounter[functionId]=1;
	}
}

# Prints statistics of seen ASDUs
function print_statistics(){
	local note = "";
	local usedIds : vector of count;
	for (id in functionIdCounter){
		usedIds[|usedIds|]=id;
	}
	usedIds = sort(usedIds);
	T104_UtilityFunctions::print_debug("",2);
	T104_UtilityFunctions::print_debug(fmt("Summary:"),2);
	T104_UtilityFunctions::print_debug(fmt("<ID>:<Count>"),2);
	for (id in usedIds){
		note= fmt("%4d: %4d",usedIds[id], functionIdCounter[usedIds[id]]);
		T104_UtilityFunctions::print_debug(note,2);
	}
}

# ASDU Event
event t104::asdu(c: connection, cause:T104_DataTypes::cause_of_transmission, infoObjectType: T104::Info_obj_code) {
	local rtuNumber=RTU_NUMBER;
	print_asdu_details(c,rtuNumber,infoObjectType);
	add_statistics(c,rtuNumber,infoObjectType);
}

# Execute after parsing whole traffic dump
event bro_done(){
	print_statistics();
}
