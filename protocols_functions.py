LENGTH_FIELD_LENGTH = 4   # Exact length of length field (in bytes)(the long of the 0009 numbers in there)
DELIMITER = "|"  # Delimiter character in protocol
DATA_DELIMITER = "#"  # Delimiter in the data part of the message


PROTOCOL_CLIENT = {
    "ask parameters":"ASK_PARAMETERS"
} # .. Add more commands if needed


PROTOCOL_SERVER = {
    "give parameters":"PARAMETERS"
} # ..  Add more commands if needed

def create_parameters_string(parameters:dict):
    final_string = ""
    for param_name in parameters:
        final_string += param_name + "-" + str(parameters[param_name]) + ","
    return final_string[:-1] # doing until -1 because we have , as the last character

def extract_parameters_from_string(parameters_string:str):
    parameters_list = parameters_string.split(",")
    parameters = {}
    for parameter_dual in parameters_list:
        key, value = parameter_dual.split("-")
        try:
            parameters[key] = int(value)
        except:
            parameters[key] = value
    return parameters