# This Bro script defines data types required for the safety boundary checks

module T104_DataTypes;

export{
	type rtu_number_t : count;
	type address_t : count;
	type normalized_value_t : double;
	type single_point_value_t : bool;
	type raw_value_t : count;

	# (rtuNo, address, normalized value) ; already converted
	type rtu_ioa_normalized_value_tuple_t:record {
		rtuNo: rtu_number_t;
		address: address_t;
		value: normalized_value_t;
	};

	# (address, normalized value) ; already converted
	type ioa_normalized_value_pair_t:record {
		address: address_t;
		value: normalized_value_t;
	};

	# (rtuNo, address, sp value) ; already converted
	type rtu_ioa_single_point_value_tuple_t:record {
		rtuNo: rtu_number_t;
		address: address_t;
		value: single_point_value_t;
	};

	# (address, sp value) ; already converted
	type ioa_single_point_value_pair_t:record {
		address: address_t;
		value: single_point_value_t;
	};

	# (rtuNo, address, value) ; raw value
	type rtu_ioa_raw_value_tuple_t:record {
		rtuNo: rtu_number_t;
		address: address_t;
		value: raw_value_t;
	};

	# (address, value) ; raw value
	type ioa_raw_value_pair_t:record {
		address: address_t;
		value: raw_value_t;
	};

	# interval of normalized - or generally double - values
	type interval_t: record{
		min : normalized_value_t &log;
		max : normalized_value_t &log;
	};

	# physical tag description from rtu config
	type physical_tag_t: record{
		tagName : string &log;
		name: string &log;
		description : string &log;
		dimension : string &log;
		normalizationInterval : interval_t &log;
	};

	# hashmap: rtu,address -> physical tag
	type physical_tag_map_t : table[rtu_number_t,address_t] of physical_tag_t;

	# log format of a physical tag
	type log_physical_tag_entry_t: record{
		ts: time &log;
		id: conn_id &log;
		note: string &log;
		physicalTag : physical_tag_t &log;
	};

	# cause of transmission information
	type cause_of_transmission:record {
		negative : bool;
		test : bool;
		common_addr : int;
	};
}