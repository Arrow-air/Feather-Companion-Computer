import socket
import pygame, math
from pygame import gfxdraw
from protocols_functions import PROTOCOL_CLIENT, PROTOCOL_SERVER,DELIMITER, LENGTH_FIELD_LENGTH, extract_parameters_from_string

pygame.init()

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5680


class D2:
    def __init__(self,modeselect:str, display_num):
        self.mode = {0:'GCS',1:'FUI'}
        self.modeselect = modeselect

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket,   socket.AF_INET = IP protocol,   socket.SOCK_STREAM = protocol TCP
            self.server_socket.connect((SERVER_IP,SERVER_PORT)) # connect to the socket(make it able to send messages in the socket)
        except:
            print("An error was raised\nThe server might be down or not started")

        if self.modeselect == self.mode.get(0):
            self.screen = pygame.display.set_mode((1860,1020), display=display_num)
            print(self.modeselect)
        elif self.modeselect == self.mode.get(1):
            self.screen = pygame.display.set_mode((1860,1020) ,display=display_num)
            print(self.modeselect)

        pygame.display.set_caption('UI Window D2')
        #pygame.display.set_icon(pygame.image.load('images/feather-icon.png'))

        self.small_font = pygame.font.SysFont('Corbel', int(self.screen.get_height()//40))
        self.medium_small_font = pygame.font.SysFont('Corbel', int(self.screen.get_height()//37.5))
        self.font = pygame.font.SysFont('Corbel', int(self.screen.get_height()//35))

        print('Display No: ' + str(pygame.display.get_num_displays()))
        print('Display Size: ' + str(pygame.display.get_window_size()))
        print('Screen size: ' + str(self.screen.get_size()))
        # both next 2 variable will be updated in the D2_func
        self.parameters = {
        }
        self.parameters_value_range = { # this is how much can the parameters move, if one has a range of -100 to 100 the value here will be 200
            
        }
        self.images = {
            "structure":pygame.image.load("images/structure.png"),
            "motor circle":pygame.image.load("images/circle image.png"),
        }
        self.images["structure"] = pygame.transform.smoothscale(self.images["structure"], ((self.images["structure"].get_width()/self.images["structure"].get_height())*self.screen.get_height()//2, self.screen.get_height()//2))
        self.images["motor circle"] = pygame.transform.smoothscale(self.images["motor circle"],(self.images["structure"].get_height()//2.1,self.images["structure"].get_height()//2.1))

        # setting up the motor images positions for faster running
        structure_size = self.images["structure"].get_size()
        structure_x = self.screen.get_width()//2 - structure_size[0]//2
        structure_y = self.screen.get_height()//2 - structure_size[1]//2
        self.motor_circle_size = self.images["motor circle"].get_size()
        self.motor_image_positions = [
            (structure_x - self.motor_circle_size[0]*0.8, structure_y - self.motor_circle_size[1]*0.8), # left top
            (structure_x - self.motor_circle_size[0]*1.1,structure_y + structure_size[1]//2 - self.motor_circle_size[1]//2), # left middle
            (structure_x - self.motor_circle_size[0]*0.8, structure_y  + structure_size[1] - self.motor_circle_size[1]//10), # left down
            (structure_x + structure_size[0] - self.motor_circle_size[0]*0.2, structure_y - self.motor_circle_size[1]*0.8), # right top
            (structure_x + structure_size[0] + self.motor_circle_size[0]*0.1, structure_y + structure_size[1]//2 - self.motor_circle_size[1]//2), # right middle
            (structure_x + structure_size[0] - self.motor_circle_size[0]*0.2, structure_y  + structure_size[1] - self.motor_circle_size[1]//10) # right down
        ]
        
    def draw_circle_info(self, motor_num,x,y,outer_circle_size, text_side):

        # BAT,ESC
        bat_value = self.parameters["BAT"+str(motor_num)+"_temp_C"]
        esc_value = self.parameters["ESC"+str(motor_num)+"_temp_C"]

        # drawing the battery color which is a ring around the motor circle
        battery_percentage = self.parameters["BAT"+str(motor_num)+"_soc_PCT"] / 100 # divide by 100 to get the percentage as a number between 0-1
        battery_ring_color = (255 - int(255*battery_percentage), int(255*battery_percentage),0)

        bat_esc_half_circle_pos = (x + self.images["motor circle"].get_width()//2,
                            y + self.images["motor circle"].get_height()//2)
        # BUT
        temp_to_max_ratio = bat_value/100
        if temp_to_max_ratio >= 1:
            temp_to_max_ratio = 1
        pygame.draw.circle(self.screen, (int(255*temp_to_max_ratio), 255 - int(255*temp_to_max_ratio),0),
                           bat_esc_half_circle_pos
                           ,outer_circle_size[0]//2, 0, draw_top_left=True,draw_bottom_left=True)
        # ESC
        temp_to_max_ratio = esc_value/100
        if temp_to_max_ratio >= 1:
            temp_to_max_ratio = 1
        pygame.draw.circle(self.screen, (int(255*temp_to_max_ratio), 255 - int(255*temp_to_max_ratio),0),
                           bat_esc_half_circle_pos
                           ,outer_circle_size[0]//2, 0, draw_top_right=True,draw_bottom_right=True)

        # drawing the border that indicates what is the battery
        circle_center = (x + outer_circle_size[0]//2, y + outer_circle_size[1]//2)
        for y2 in range(int(y - outer_circle_size[1]*0.2),int(y+outer_circle_size[1]*1.2)):
            for x2 in range(int(x - outer_circle_size[0]*0.2), int(x+outer_circle_size[0]*1.2)):
                distance_from_center = math.sqrt(math.pow(circle_center[0] - x2,2)+math.pow(circle_center[1] - y2,2))
                if distance_from_center >= outer_circle_size[0]//2 and distance_from_center <=  outer_circle_size[0]*(2.3/4):
                    d_y2_y = y2 - y
                    ratio_to_size = d_y2_y/outer_circle_size[1]
                    if ratio_to_size <= battery_percentage:
                        self.screen.set_at((x2,y2),battery_ring_color)

        # blitting the motor circle 
        self.screen.blit(self.images["motor circle"], (x,y))

        # rpm text
        self.screen.blit(self.small_font.render(str(self.parameters["MOT"+str(motor_num)+"_rpm_PCT"]),True,(0,0,0)), (x + outer_circle_size[0]//2 - self.small_font.size(str(self.parameters["MOT"+str(motor_num)+"_rpm_PCT"]))[0]//2,y + outer_circle_size[1]//2 - self.small_font.size("R")[1]))
        self.screen.blit(self.small_font.render("RPM",True,(100,100,100)), (x + outer_circle_size[0]//2 - self.small_font.size("RPM")[0]//2,y + outer_circle_size[1]//2))
        
        # BAT text
        BAT_text = str(bat_value) + "C"
        self.screen.blit(self.medium_small_font.render(BAT_text,True,(0,0,0)), (x + outer_circle_size[0]//2 - self.medium_small_font.size(BAT_text+"aa.")[0], y + outer_circle_size[1]//2+self.medium_small_font.size("A")[1]*1.1))
        self.screen.blit(self.medium_small_font.render("BAT",True,(0,0,0)), (x + outer_circle_size[0]//2 - self.medium_small_font.size("BAT"+"ab")[0], y + outer_circle_size[1]//2+self.medium_small_font.size("A")[1]*2.1))
        
        # ESC text
        ESC_text = str(esc_value) + "C"
        self.screen.blit(self.medium_small_font.render(ESC_text,True,(0,0,0)), (x + outer_circle_size[0]//2 + self.medium_small_font.size("aa.")[0], y + outer_circle_size[1]//2+self.medium_small_font.size("A")[1]*1.1))
        self.screen.blit(self.medium_small_font.render("ESC",True,(0,0,0)), (x + outer_circle_size[0]//2 + self.medium_small_font.size("ab")[0], y + outer_circle_size[1]//2+self.medium_small_font.size("A")[1]*2.1))

        # the text on the side
        if text_side =='l': # left side of the circle
            text_x = x - self.font.size("Volt: 12345")[0]
            self.screen.blit(self.font.render("Volt: "+str(self.parameters["ESC"+str(motor_num)+"_V"]),True,(255,255,255)), (text_x, y + outer_circle_size[1]//2 - self.font.size("V")[1]))
            self.screen.blit(self.font.render("Cur: "+str(self.parameters["ESC"+str(motor_num)+"_CUR_AMP"]),True,(255,255,255)), (text_x, y + outer_circle_size[1]//2))
            self.screen.blit(self.font.render("Power: "+str(self.parameters["ESC"+str(motor_num)+"_CUR_AMP"]*self.parameters["ESC"+str(motor_num)+"_V"]),True,(255,255,255)), (text_x, y + outer_circle_size[1]//2 + self.medium_small_font.size("P")[1]))
        else: # right side of the circle
            text_x = x + outer_circle_size[0] + self.font.size("45")[0]
            self.screen.blit(self.font.render("Volt: "+str(self.parameters["ESC"+str(motor_num)+"_V"]),True,(255,255,255)), (text_x, y + outer_circle_size[1]//2 - self.font.size("V")[1]))
            self.screen.blit(self.font.render("Cur: "+str(self.parameters["ESC"+str(motor_num)+"_CUR_AMP"]),True,(255,255,255)), (text_x, y + outer_circle_size[1]//2))
            self.screen.blit(self.font.render("Power: "+str(self.parameters["ESC"+str(motor_num)+"_CUR_AMP"]*self.parameters["ESC"+str(motor_num)+"_V"]),True,(255,255,255)), (text_x, y + outer_circle_size[1]//2 + self.medium_small_font.size("P")[1]))
        
    def draw(self):
        self.screen.fill((65, 95, 255))
        
        # structure
        structure_size = self.images["structure"].get_size()
        structure_x = self.screen.get_width()//2 - structure_size[0]//2
        structure_y = self.screen.get_height()//2 - structure_size[1]//2
        self.screen.blit(self.images["structure"], (structure_x,structure_y))

        # left top
        x,y = self.motor_image_positions[0]
        pygame.draw.line(self.screen, (255,255,255), (x+self.motor_circle_size[0]*0.85,y+self.motor_circle_size[1]*0.85), (x+self.motor_circle_size[0]*1.1,y+self.motor_circle_size[1]*1.1),10)
        self.draw_circle_info(1,x,y,self.motor_circle_size,'l')

        # left middle
        x,y = self.motor_image_positions[1]
        pygame.draw.line(self.screen, (255,255,255), (x+self.motor_circle_size[0]*0.9,y+self.motor_circle_size[1]//1.4), (x+self.motor_circle_size[0]*1.11,y+self.motor_circle_size[1]//1.4),10)
        self.draw_circle_info(3,x,y,self.motor_circle_size,'l')
        
        # left down
        x,y = self.motor_image_positions[2]
        pygame.draw.line(self.screen, (255,255,255), (x+self.motor_circle_size[0]*0.75,y + self.motor_circle_size[1]*0.1), (x+self.motor_circle_size[0]*0.9,y - self.motor_circle_size[1]*0.1),10)
        self.draw_circle_info(5,x,y,self.motor_circle_size,'l')

        # right top
        x,y = self.motor_image_positions[3]
        pygame.draw.line(self.screen, (255,255,255), (x+self.motor_circle_size[0]*0.15,y+self.motor_circle_size[1]*0.85), (x-self.motor_circle_size[0]*0.1,y+self.motor_circle_size[1]*1.1),10)
        self.draw_circle_info(2,x,y,self.motor_circle_size,'r')

        # right middle
        x,y = self.motor_image_positions[4]
        pygame.draw.line(self.screen, (255,255,255), (x+self.motor_circle_size[0]*0.1,y+self.motor_circle_size[1]//1.4), (x-self.motor_circle_size[0]*0.11,y+self.motor_circle_size[1]//1.4),10)
        self.draw_circle_info(4,x,y,self.motor_circle_size,'r')

        # right down
        x,y = self.motor_image_positions[5]
        pygame.draw.line(self.screen, (255,255,255), (x+self.motor_circle_size[0]*0.25,y + self.motor_circle_size[1]*0.1), (x+self.motor_circle_size[0]*0.1,y - self.motor_circle_size[1]*0.1),10)
        self.draw_circle_info(6,x,y,self.motor_circle_size,'r')
      
    def build_message(self,cmd, data):
        """
        Gets command name (str) and data field (str) and creates a valid protocol message
        Returns: str, or None if error occured
        example of the function:
        build_message("LOGIN", "aaaa#bbbb") will return "LOGIN           |0009|aaaa#bbbb"
        """
        """get the command plus data and return the protocol message(what parse_message gets)"""

        protocol_message = ""
        num = len(data)
        if len(str(num)) < LENGTH_FIELD_LENGTH: # create the message and the message length(009,0100)
            num1 = LENGTH_FIELD_LENGTH - len(str(num))
            num = "0"*num1 + str(num)
        protocol_message += str(cmd) + DELIMITER + num + DELIMITER + str(data) # implement everything you did in the function to the protocol that send   DELIMITER = |

        return protocol_message
    def build_and_send_message(self,conn, code, data): # code = command
        message = self.build_message(code,data) # create the message( will look like this: LOGIN           |0009|aaaa#bbbb)
        
        print("[CLIENT]:", message)
        
        conn.send(message.encode()) # send to the server the message in the right format
    def parse_message(self,data):
        """
        Parses protocol message and returns command name and data field
        Returns: cmd (str), data (str). If some error occured, returns None, None
        """
        "get the message(what build_message returns) and need to return the command and the data"
        split_data = data.split(DELIMITER)
        cmd,length,data = split_data
        return cmd,data
    def recv_message_and_parse(self,conn):
        full_msg = conn.recv(1024).decode() # gets the message from the server   need to be something like this for example "LOGIN           |0009|aaaa#bbbb"
        cmd, data = self.parse_message(full_msg) # split it to a tuple with the command and the data
        
        print("[SERVER]:", full_msg)
        return cmd, data
    
    def send_and_receive_message(self):
        self.build_and_send_message(self.server_socket, "MESSAGE", "test")

        command,data = self.recv_message_and_parse(self.server_socket)
    def receive_parameters(self):
        self.build_and_send_message(self.server_socket, PROTOCOL_CLIENT["ask parameters"], "")
        cmd,data = self.recv_message_and_parse(self.server_socket)
        if cmd == PROTOCOL_SERVER["give parameters"]:
            self.parameters = extract_parameters_from_string(data)


def D2_func(parameters_dict, display_num):
    D2_ui = D2("FUI",display_num)
    # update the class parameters
    D2_ui.parameters = parameters_dict

    print("Connected to the server: [SERVER]"+str(SERVER_IP)+":"+str(SERVER_PORT))

    running = True
    while running:
        D2_ui.receive_parameters()
        D2_ui.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False


        pygame.display.update()

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

    "BAT1_temp_C":90, # warning range: 80-180
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

if __name__ == '__main__':
    D2_func(parameters, 1)
