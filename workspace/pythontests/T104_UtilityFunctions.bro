# This Bro script provides several utility functions like logging

@load T104_DataTypes
module T104_UtilityFunctions;

export{
	const DEBUG_ENABLED = T &redef;
	const DEBUG_LEVEL = 1 &redef; # 1... verbose, 2... less verbose
	const DEBUG_PRINT_LEVEL = F &redef;

	# Debug output
	function print_debug(message : string, level : int &default=1){
		if (DEBUG_ENABLED && level>=DEBUG_LEVEL){
			if (DEBUG_PRINT_LEVEL){
				print fmt("[DEBUG L%d] %s",level,message);
			}
			else {
				print fmt("%s",message);
			}
		}
	}

	# Format a physical tag
	function get_physical_tag_note(rtuNumber : T104_DataTypes::rtu_number_t, address : T104_DataTypes::address_t, current_physical_tag : T104_DataTypes::physical_tag_t, printNormalizationInterval : bool &default=F) : string {
		if(printNormalizationInterval){
			return fmt("<RTU: %d, Address: %d, Tag: %s, Name: %s, Description: %s, Unit: %s, Normalization interval: [%f,%f]>",rtuNumber,address,current_physical_tag$tagName,current_physical_tag$name,current_physical_tag$description,current_physical_tag$dimension,current_physical_tag$normalizationInterval$min,current_physical_tag$normalizationInterval$max); 
		} else {
			return fmt("<RTU: %d, Address: %d, Tag: %s, Name: %s, Description: %s, Unit: %s>",rtuNumber,address,current_physical_tag$tagName,current_physical_tag$name,current_physical_tag$description,current_physical_tag$dimension); 		
		}
	}

	# Format a timestamp
	function format_timestamp(timestamp : time):string {
		return strftime("%Y-%m-%d %H:%M:%S", timestamp);
	}

	# Convert raw value from bro event into normalized value between -1.0 and 1.0
	function normalize_value(raw : T104_DataTypes::raw_value_t):T104_DataTypes::normalized_value_t {
		local tmpValue : T104_DataTypes::normalized_value_t = raw/32768.0;
		if(tmpValue<=1.0) {
			# positive value
			return tmpValue;
		} else {
			# negative value
			return tmpValue-2;
		}
	}

	# Denormalize value from a normalized value between -1.0 and 1.0 into real float value
	function denormalize_value(normalized_value : T104_DataTypes::normalized_value_t,normalization_interval : T104_DataTypes::interval_t):T104_DataTypes::normalized_value_t {
		local interval_position = (normalized_value + 1)/2.0;
		local difference = normalization_interval$max - normalization_interval$min;
		return normalization_interval$min + difference * interval_position;
	}

	# This function is from T104_DoubleTests.bro
	function doublefy_value_test(raw : T104_DataTypes::raw_value_t):T104_DataTypes::normalized_value_t {
    local command = fmt("/data/scripts/DoubleConverterC++ %d",raw);
    local cmd = Exec::Command($cmd=command);
    when (local res = Exec::run(cmd))
    {
    				return to_double(res$stdout[0]);
    }  
    return -1.0;
	}	

	# Convert raw double value from bro event into a double value (this is damn slow, no bro builtin for that available)
	function doublefy_value(raw : T104_DataTypes::raw_value_t):T104_DataTypes::normalized_value_t {
		return doublefy_value_test(raw);		
	}

	# Interval check (inclusive edges) for normalized (or generally double) values
	function interval_check(value: T104_DataTypes::normalized_value_t,allowed_interval: T104_DataTypes::interval_t) : bool{
	  return (allowed_interval$min <= value && value <= allowed_interval$max); 
	}

}