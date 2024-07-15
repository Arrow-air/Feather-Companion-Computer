LENGTH_FIELD_LENGTH = 4   # Exact length of length field (in bytes)(the long of the 0009 numbers in there)
DELIMITER = "|"  # Delimiter character in protocol
DATA_DELIMITER = "#"  # Delimiter in the data part of the message


PROTOCOL_CLIENT = {
    "ask parameters":"ASK_PARAMETERS"
} # .. Add more commands if needed


PROTOCOL_SERVER = {
    "give parameters":"PARAMETERS"
} # ..  Add more commands if needed

KEY_DATA_DELIMITER = "="

def create_parameters_string(parameters:dict):
    final_string = ""
    for param_name in parameters:
        final_string += param_name + KEY_DATA_DELIMITER + str(parameters[param_name]) + ","
        
    return final_string[:-1] # doing until -1 because we have , as the last character

def create_parameters_string(parameters:dict):
    strings = ["",""]
    i = 0
    for param_name in parameters:
        if i == 0:
            strings[0] += param_name + KEY_DATA_DELIMITER + str(parameters[param_name]) + ","
            #final_string += param_name + KEY_DATA_DELIMITER + str(parameters[param_name]) + ","
            i += 1
        else:
            strings[1] += param_name + KEY_DATA_DELIMITER + str(parameters[param_name]) + ","
            i = 0
    strings[0] = strings[0][:-1]
    strings[1] = strings[1][:-1]
    return strings
    final_string = ""
    for param_name in parameters:
        final_string += param_name + KEY_DATA_DELIMITER + str(parameters[param_name]) + ","
        
    return final_string[:-1] # doing until -1 because we have , as the last character


def extract_parameters_from_string(parameters_string:str):
    parameters_list = parameters_string.split(",")
    parameters = {}
    for parameter_dual in parameters_list:
        key, value = parameter_dual.split(KEY_DATA_DELIMITER)
        try:
            parameters[key] = int(value)
        except:
            try:
                parameters[key] = float(value)
            except:
                parameters[key] = value
    return parameters