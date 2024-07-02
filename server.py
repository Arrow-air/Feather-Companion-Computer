##############################################################################
# server.py
##############################################################################

import socket,select
from protocols_functions import PROTOCOL_CLIENT, PROTOCOL_SERVER,DELIMITER, LENGTH_FIELD_LENGTH, create_parameters_string

global messages_to_send
messages_to_send = [] # (client IP+port, message(LOGIN_ok        |0012|aaaa#bbbb))

SERVER_PORT = 5680
SERVER_IP = "127.0.0.1"


global parameters
parameters = {
    "altitude_AGL":0,
    "altitude_AGL_set":0,
    "altitude_ABS":0,
    "heading":0,
    "compass":0,
    "attitude_pitch":0, # forward-backward rotation of the aircraft itself, in what angle the aircraft is leaning to forward or backward, range: -180 to 180(minus is leaning backward, positive is leaning forward)
    "attitude_roll":0, # right-left rotation of the aircraft itself, in what angle the aircraft is leaning side wise, range: -180 to 180(minus is leaning to the left side, positive is to the right side)
    "vertical_speed_KTS":0,
    "airspeed_KTS":0, # warning range: 55-60,-60-(-55), [kts], speed will be between 0-60 knots
    "OAT":0, # warning range: 30-max=100
    "latitude":"""40° 26' 46" N""",
    "longitude":"""79° 58' 56" W""",
    "flight_time":"38:15",
    "command_pitch":0, # right joystick, up-down, range: -1 to 1
    "command_roll":0, # right joystick, left-right, range: -1 to 1
    "command_throttle":0, # left joystick, up-down, range: -1 to 1
    "command_yaw":0, # left joystick, left-right, range: -1 to 1
    "switch_states":0,
    "parachute_state":0,

    "BAT1_temp_C":0, # warning range: 80-180
    "BAT2_temp_C":10, # warning range: 80-180
    "BAT3_temp_C":40, # warning range: 80-180
    "BAT4_temp_C":90, # warning range: 80-180
    "BAT5_temp_C":85, # warning range: 80-180
    "BAT6_temp_C":50, # warning range: 80-180

    "ESC1_temp_C":60,
    "ESC2_temp_C":70,
    "ESC3_temp_C":20,
    "ESC4_temp_C":40,
    "ESC5_temp_C":10,
    "ESC6_temp_C":30,

    "MOT1_temp_C":0,
    "MOT2_temp_C":0,
    "MOT3_temp_C":0,
    "MOT4_temp_C":0,
    "MOT5_temp_C":0,
    "MOT6_temp_C":0,

    "BAT1_soc_PCT":12, # the percentage of the battery left, warning range: 1-15
    "BAT2_soc_PCT":100, # the percentage of the battery left, warning range: 1-15
    "BAT3_soc_PCT":100, # the percentage of the battery left, warning range: 1-15
    "BAT4_soc_PCT":57, # the percentage of the battery left, warning range: 1-15
    "BAT5_soc_PCT":80, # the percentage of the battery left, warning range: 1-15
    "BAT6_soc_PCT":40, # the percentage of the battery left, warning range: 1-15

    "MOT1_rpm_PCT":130, # warning range: 120-max=140
    "MOT2_rpm_PCT":0, # warning range: 120-max=140
    "MOT3_rpm_PCT":0, # warning range: 120-max=140
    "MOT4_rpm_PCT":0, # warning range: 120-max=140
    "MOT5_rpm_PCT":0, # warning range: 120-max=140
    "MOT6_rpm_PCT":0, # warning range: 120-max=140

    "ESC1_V":0,
    "ESC2_V":0,
    "ESC3_V":0,
    "ESC4_V":0,
    "ESC5_V":0,
    "ESC6_V":0,
    
    "ESC1_CUR_AMP":0,
    "ESC2_CUR_AMP":0,
    "ESC3_CUR_AMP":0,
    "ESC4_CUR_AMP":0,
    "ESC5_CUR_AMP":0,
    "ESC6_CUR_AMP":0,
    "TimeStamp":0
}



def setup_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket,   socket.AF_INET = IP protocol,   socket.SOCK_STREAM = protocol TCP
    sock.bind((SERVER_IP,SERVER_PORT)) # 
    sock.listen() # listen to sockets
    return sock

def build_message(cmd, data):
    protocol_message = ""
    num = len(data)
    if len(str(num)) < LENGTH_FIELD_LENGTH: # create the message and the message length(009,0100)
        num1 = LENGTH_FIELD_LENGTH - len(str(num))
        num = "0"*num1 + str(num)
    protocol_message += str(cmd) + DELIMITER + num + DELIMITER + str(data) # implement everything you did in the function to the protocol that send   DELIMITER = |

    return protocol_message

def build_and_send_message(conn, code, msg):
    message = build_message(code,msg) # create the message( will look like this: LOGIN_OK        |0012|aaaa#bbbb)
    messages_to_send.append((conn, message))
    print(f"[SERVER] msg to{conn.getpeername()}: ",message)	  # Debug print

def parse_message(data):
    """
	Parses protocol message and returns command name and data field
	Returns: cmd (str), data (str). If some error occured, returns None, None
	"""
    "get the message(what build_message returns) and need to return the command and the data"
    split_data = data.split("|")
    
    cmd,length,data = split_data
    return cmd,data

def recv_message_and_parse(conn):
    full_msg = conn.recv(8192).decode() # gets the message from the server   need to be something like this for example "LOGIN           |0009|aaaa#bbbb"
    if full_msg == "":
        return None, None
    cmd, data = parse_message(full_msg) # split it to a tuple with the command and the data
    print(f"[CLIENT] {conn.getpeername()} msg: ",full_msg)  # Debug print
    return cmd, data
	
def handle_client_message(conn, cmd, data):
    global parameters
    if cmd == PROTOCOL_CLIENT["ask parameters"]:
        parameters_string = create_parameters_string(parameters) #",".join(list(parameters))
        build_and_send_message(conn, PROTOCOL_SERVER["give parameters"],parameters_string)
    else:
        build_and_send_message(conn,cmd,data)

server_socket = setup_socket()
client_sockets = []
i = 0
"""
server_loop_iteration(): instead of doing the code inside the function inside a while loop and it will stop a program that runs in the background
this function serves as 1 iteration of the while loop and now we have the option to do the loop in the required wanted speed"""
def server_loop_iteration(parameters_updated):
    global parameters, messages_to_send, i
    parameters = parameters_updated

    ready_to_read, ready_to_write, in_error = select.select([server_socket] + client_sockets, [],[])
    
    for current_socket in ready_to_read: # a loop that go over all of the sockets you can read from
        if current_socket is server_socket: # if the current socket is the server socket(if a new client arrived)
            
            (client_socket, client_address) = current_socket.accept() # get the client socket and the client IP/create a conaction with the client
            print("New client joined!",client_address)
            client_sockets.append(client_socket) # append to the sockets list new client socket
            
        else: # if the server got new message
            
            #print("New data from client")
            try:
                cmd,data = recv_message_and_parse(current_socket) # gets the command+data
                if cmd == None or cmd == "" and data == "": # closes the socket
                    client_sockets.remove(current_socket)
                    current_socket.close()
                    print(current_socket.getpeername(),"disconnect, socket closed")
                handle_client_message(current_socket, cmd,data)
            except Exception as e: # if it got error (will be ConnectionResetError if the client closed the cmd window)
               
                #print("Error user closed cmd window\n",e)
                try: # trying to logout
                    # doing it because if the client just close the window it wont do the logout
                    client_sockets.remove(current_socket)
                    current_socket.close()
                    print(current_socket.getpeername(),"disconnect, socket closed")
                except: # gives an error if the socket is already closed
                    pass
                
    for message1 in messages_to_send:
        socket1 = message1[0]
        message = message1[1]
        try:
            socket1.send(message.encode())
        except:
            pass
    messages_to_send = []

def main():	
    print("Server is up and running")

    while True:
        server_loop_iteration(parameters)



if __name__ == '__main__':
    main()
