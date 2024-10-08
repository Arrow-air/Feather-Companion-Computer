import socket
import pygame
from pygame import gfxdraw
from protocols_functions import PROTOCOL_CLIENT, PROTOCOL_SERVER,DELIMITER, LENGTH_FIELD_LENGTH, extract_parameters_from_string

pygame.init()

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5680


class D1:
    def __init__(self,modeselect:str, display_num):
        self.mode = {0:'GCS',1:'FUI'}
        self.modeselect = modeselect

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket,   socket.AF_INET = IP protocol,   socket.SOCK_STREAM = protocol TCP
            self.server_socket.connect((SERVER_IP,SERVER_PORT)) # connect to the socket(make it able to send messages in the socket)
        except:
            pass

        if self.modeselect == self.mode.get(0):
            self.screen = pygame.display.set_mode((1860,1020), display=display_num)
            print(self.modeselect)
        elif self.modeselect == self.mode.get(1):
            self.screen = pygame.display.set_mode((1860,1020) ,display=display_num)
            print(self.modeselect)

        pygame.display.set_caption('UI Window D1')
        #pygame.display.set_icon(pygame.image.load('images/feather-icon.png'))

        self.font = pygame.font.SysFont('Corbel', int(self.screen.get_height()//30))
        self.medium_font = pygame.font.SysFont('Corbel', int(self.screen.get_height()//25))
        self.bigger_font = pygame.font.SysFont('Corbel', int(self.screen.get_height()//15))

        print('Display No: ' + str(pygame.display.get_num_displays()))
        print('Display Size: ' + str(pygame.display.get_window_size()))
        print('Screen size: ' + str(self.screen.get_size()))
        # both next 2 variable will be updated in the D1_func
        self.parameters = {
        }
        self.parameters_value_range = { # this is how much can the parameters move, if one has a range of -100 to 100 the value here will be 200
            "airspeed_KTS":60
        }

        self.images = {
            "compass":pygame.transform.smoothscale(pygame.image.load("images/compass.png"),(self.screen.get_height()//3.5*1.2,self.screen.get_height()//3.5*1.2)),
            "roll":pygame.transform.smoothscale(pygame.image.load("images/roll image.png"),(self.screen.get_height()//3.5*1.2,self.screen.get_height()//3.5*1.2)),
            "pointer above roll":pygame.image.load("images/pointer above roll.png"),
            "pointer":pygame.image.load("images/pointer.png")
        }
        roll_pointer_ratio = self.images["pointer above roll"].get_height() / self.images["pointer above roll"].get_width()
        self.images["pointer above roll"] = pygame.transform.smoothscale(self.images["pointer above roll"], (self.screen.get_height()//3.5,self.screen.get_height()//3.5*roll_pointer_ratio))
        self.images["pointer"] = pygame.transform.smoothscale(self.images["pointer"], (self.images["compass"].get_width()//10,self.images["compass"].get_width()//10))
    
    def check_for_warning(self):
        warning_variables = []

        for key, value in self.parameters.items():
            if key.endswith('_KTS'):
                if abs(value) >= 55 and abs(value) <= 60:
                    warning_variables.append(key)
            elif key.endswith('_temp_C'):
                if value >= 80 and value <= 180:
                    warning_variables.append(key)
            elif key.endswith('_soc_PCT'):
                if value >= 1 and value <= 15:
                    warning_variables.append(key)
            elif key.endswith('_rpm_PCT'):
                if value >= 120 and value <= 140:
                    warning_variables.append(key)
            elif key == 'OAT':
                if value >= 30 and value <= 100:
                    warning_variables.append(key)

        return warning_variables

    def draw_transparent_rect(self,win,size,alpha_level,color,pos, border_width = None, border_radius=5):
        transparent_surface = pygame.Surface((size[0], size[1]), pygame.SRCALPHA)
        if border_width == None:
            pygame.draw.rect(transparent_surface,(color[0],color[1],color[2],alpha_level) , (0, 0, size[0], size[1]), border_radius=border_radius)
        else:
            pygame.draw.rect(transparent_surface,(color[0],color[1],color[2],alpha_level) , (0, 0, size[0], size[1]), border_width, border_radius=border_radius)
        win.blit(transparent_surface, (pos[0],pos[1]))

    def draw(self):
        self.screen.fill((65, 95, 255))

        # show the warnings
        # warning are on the Left screen(Left part of the window)(D1)
        warnings = self.check_for_warning()
        if warnings != []:
            #warnings = ", ".join(warnings)
            #text = "Warning: " + warnings + " has exceeded tolerance!"
            text = "Warning: " + ", ".join(warnings) + " has exceeded tolerance!"

            max_text_width = self.screen.get_width()//5*4
            x =  self.screen.get_width() - max_text_width - self.bigger_font.size("5")[0] # the warnings are on the right part of the first screen(D1), doing minus the size of 5 because there are the lines of the height and this is how they are made
            y = 20 # leaving space for the speed text

            current_text = ""
            text_lines = []
            # splitting the text into lines because it is too long for 1 line sometimes
            for word in text.split(" "):
                # if text is too long
                if self.font.size(current_text+" " + word)[0] > max_text_width:
                    text_lines.append(current_text)
                    current_text = word
                # if text is not too long
                else:
                    current_text += word + " "
                    if word == text.split(" ")[-1]:
                        text_lines.append(current_text)

            max_length_text = max(text_lines, key=len)
            if max_length_text[-1] == " ":
                max_length_text = max_length_text[:-1]

            # drawing the square behind the text
            pygame.draw.rect(self.screen,(200,200,200),[x - self.font.size("a")[0],y,  # x, y
                                                        max_text_width, # width
                                                        (len(text_lines)+1)*(self.font.size("A")[1]) # height
                                                        ],
                             border_top_left_radius = 10, border_top_right_radius = 10, border_bottom_left_radius = 10, border_bottom_right_radius = 10) # round corners with the radius of 10
            pygame.draw.rect(self.screen,(0,0,0),[x - self.font.size("a")[0],y, # x,y
                                                max_text_width, # width
                                                (len(text_lines)+1)*(self.font.size("A")[1]) # height
                                                ],2, # width of the line of the rect(rect of only outer line)
                                                10,10,10,10) # round corners with the radius of 10
            y += self.font.size("a")[1]//2 # adding to the y for it to look better
            # blit text by lines and y changes
            for line_text in text_lines:
                self.screen.blit(self.font.render(line_text,True,(0,0,0)),(x,y))
                y += self.font.size("A")[1]

        # aircraft speed:
        # placing the line above the text to show how fast the aircraft is compare to it's max
        speed_bar_x = 0 + self.font.size("a")[0]//2
        speed_bar_width = self.screen.get_width()/20*19
        speed_bar_height = self.font.size("a")[1]//2
        self.draw_transparent_rect(self.screen,(speed_bar_width,speed_bar_height),100,(200,200,200),(speed_bar_x,5))
        self.draw_transparent_rect(self.screen,(speed_bar_width,speed_bar_height),100,(255,255,255),(speed_bar_x,5),1)
        pygame.draw.rect(self.screen, (255,255,255), [speed_bar_x, 5, speed_bar_width*(abs(self.parameters["airspeed_KTS"])/ self.parameters_value_range["airspeed_KTS"]), speed_bar_height], border_radius=5)

        # placing the text of the speed with it's units
        # not using text y variable for faster running time
        self.screen.blit( self.bigger_font.render( str(round(self.parameters["airspeed_KTS"],1)), True,(255,255,255) ) , (self.bigger_font.size("5")[0]//2,20))
        self.screen.blit( self.font.render( "m/s", True,(255,255,255) ) , (self.bigger_font.size("5")[0]//2,20 + self.bigger_font.size("5")[1]))

        # aircraft height variables(bar variables):
        num_of_lines = 29 # 1 on the text y, 9 below and 9 above
        line_width = self.bigger_font.size("5")[0]
        line_height = 2
        space_between_lines = self.screen.get_height()//(num_of_lines-1)
        height_lines_y = [self.screen.get_height()//2]
        for y in range(height_lines_y[0],0,-space_between_lines-line_height):
            height_lines_y.append(y)
        for y in range(height_lines_y[0],self.screen.get_height(),+space_between_lines+line_height):
            height_lines_y.append(y)
        lines_x = self.screen.get_width() -  line_width*1.2
        height_lines_y = sorted(height_lines_y)
        
        # aircraft height text bliting
        self.screen.blit(self.bigger_font.render(str(round(self.parameters["altitude_AGL"],1))+"m", True, (255,255,255)), 
                         (self.screen.get_width() - line_width*2.6 - self.bigger_font.size(str(round(self.parameters["altitude_AGL"],1))+"m")[0],self.screen.get_height()//2 - self.bigger_font.size("f")[1]//2)
                         )
        
        # aircraft height bar
        a = 0 # the alpha level(transparency value)
        a_goes_up = True
        for line_y in height_lines_y:
            if line_y == self.screen.get_height()//2: # if the middle line(the one which is on the numbers)
                # drawing a line without alpha level
                pygame.draw.rect(self.screen, (255,255,255,255), [lines_x - line_width,line_y,line_width*2,line_height])
                a_goes_up = False
            else: # the lines with the alpha level
                self.draw_transparent_rect(self.screen, (line_width,line_height),a,(255,255,255),(lines_x,line_y))
                # if it is above the middle line
                if a_goes_up == True: # will add to the alpha level by the number of lines
                    a += 255//((num_of_lines-2)//2)
                    if a > 255:
                        a = 255
                # if it is below the middle line
                else: # will decrease to the alpha level by the number of lines
                    a -= 255//((num_of_lines-2)//2)
                    if a < 0:
                        a = 1

        # The joysticks + flight time

        # left joystick
        joystick_size = self.screen.get_height()//5
        joystick_width = joystick_size//10
        joystick_x = joystick_size*2
        joystick_y = self.screen.get_height() - joystick_size
        self.draw_transparent_rect(self.screen,(joystick_size,joystick_width),100,(255,255,255),(joystick_x,joystick_y))
        self.draw_transparent_rect(self.screen,(joystick_size,joystick_width),200,(255,255,255),(joystick_x,joystick_y),2)
        self.draw_transparent_rect(self.screen,(joystick_width,joystick_size),100,(255,255,255),(joystick_x + joystick_size//2 - joystick_width//2,joystick_y - joystick_size//2 + joystick_width//2))
        self.draw_transparent_rect(self.screen,(joystick_width,joystick_size),200,(255,255,255),(joystick_x + joystick_size//2 - joystick_width//2,joystick_y - joystick_size//2 + joystick_width//2),2)
        circle_x = joystick_x + joystick_size//2 + (joystick_size //2) * (round(float(self.parameters["command_yaw"]),1))
        circle_y = joystick_y + joystick_width//2 - (joystick_size //2) * (round(float(self.parameters["command_throttle"]),1))
        gfxdraw.filled_circle(self.screen, int(circle_x), int(circle_y),joystick_width,(255,255,255,100))
        gfxdraw.filled_circle(self.screen, int(circle_x), int(circle_y),joystick_width//2,(255,255,255,255))
        pygame.draw.circle(self.screen,(255,255,255),(int(circle_x), int(circle_y)),joystick_width,1)
        self.screen.blit(self.medium_font.render("Y",True,(255,255,255)), (joystick_x - self.medium_font.size("Y")[0]*1.5, joystick_y))
        self.screen.blit(self.medium_font.render("T",True,(255,255,255)), (joystick_x + joystick_size//2 - self.medium_font.size("T")[0]//2, joystick_y - joystick_size//2 - self.medium_font.size("T")[0]*1.5))
        
        # flight time, positioned between the joysticks
        time_text = (self.parameters["flight_time"].split(":")[0]+"m") + ":" + (self.parameters["flight_time"].split(":")[1]+"s")
        time_text_x = joystick_x + joystick_size*1.5
        self.screen.blit(self.bigger_font.render(time_text, True, (255,255,255)), (time_text_x, joystick_y))
        self.screen.blit(self.medium_font.render("Flight Time Remaining", True, (255,255,255)), (time_text_x, joystick_y + self.bigger_font.size("1")[1]))

        # right joystick
        joystick_x =  time_text_x + self.medium_font.size("Flight Time Remaining")[0] + joystick_size*0.5 # using the height text position and the time text x and size
        self.draw_transparent_rect(self.screen,(joystick_size,joystick_width),100,(255,255,255),(joystick_x,joystick_y))
        self.draw_transparent_rect(self.screen,(joystick_size,joystick_width),200,(255,255,255),(joystick_x,joystick_y),2)
        self.draw_transparent_rect(self.screen,(joystick_width,joystick_size),100,(255,255,255),(joystick_x + joystick_size//2 - joystick_width//2,joystick_y - joystick_size//2 + joystick_width//2))
        self.draw_transparent_rect(self.screen,(joystick_width,joystick_size),200,(255,255,255),(joystick_x + joystick_size//2 - joystick_width//2,joystick_y - joystick_size//2 + joystick_width//2),2)
        circle_x = joystick_x + joystick_size//2 + (joystick_size //2) * (round(float(self.parameters["command_roll"]),1))
        circle_y = joystick_y + joystick_width//2 - (joystick_size //2) * (round(float(self.parameters["command_pitch"]),1))
        gfxdraw.filled_circle(self.screen, int(circle_x), int(circle_y),joystick_width,(255,255,255,100))
        gfxdraw.filled_circle(self.screen, int(circle_x), int(circle_y),joystick_width//2,(255,255,255,255))
        pygame.draw.circle(self.screen,(255,255,255),(int(circle_x), int(circle_y)),joystick_width,1)
        self.screen.blit(self.medium_font.render("R",True,(255,255,255)), (joystick_x - self.medium_font.size("Y")[0]*1.5, joystick_y))
        self.screen.blit(self.medium_font.render("P",True,(255,255,255)), (joystick_x + joystick_size//2 - self.medium_font.size("T")[0]//2, joystick_y - joystick_size//2 - self.medium_font.size("T")[0]*1.5))

        # latitude and longitude text
        position_in_angle_text_pos = (5, joystick_y - joystick_size*2)
        self.screen.blit(self.medium_font.render("Lat: " + self.parameters["latitude"], True, (255,255,255)),(position_in_angle_text_pos[0],position_in_angle_text_pos[1]-self.medium_font.size("L")[1]))
        self.screen.blit(self.medium_font.render("Long: " + self.parameters["longitude"], True, (255,255,255)),(position_in_angle_text_pos[0],position_in_angle_text_pos[1]+self.medium_font.size("L")[1]))
        
        # rotate forward representation, attitude pitch
        pitch_angle = round(self.parameters["attitude_pitch"],1)
        line_size = (self.images["compass"].get_width()//3*1.2, self.images["compass"].get_width()//3//8)
        pitch_x = position_in_angle_text_pos[0] +self.medium_font.size("Long: " + self.parameters["longitude"]+"AA")[0] #line_size[0]
        pitch_y = joystick_y - joystick_size*2
        
        # define and draw the rect around it
        rect_around_pitch_size = (line_size[0]*2, line_size[0]*3)
        self.draw_transparent_rect(self.screen, rect_around_pitch_size,200,(255,255,255), (pitch_x, pitch_y-rect_around_pitch_size[1]//2), 1)
        
        # draw the text above it that states what it is
        self.screen.blit(self.medium_font.render("Attitude Pitch",True,(255,255,255)),(pitch_x, pitch_y-rect_around_pitch_size[1]//2 - self.medium_font.size("A")[1]*1.1))
        
        # Drawing the lines
        # drawing the lines that shown the angle using the ratio
        closest_above_round = pitch_angle + (10 -(pitch_angle%10)) # closest number above the current angle
        closest_below_round = pitch_angle - (pitch_angle%10) # closest number below the current angle
        space_between_lines = line_size[0]//2
        above_center_y = pitch_y - space_between_lines*((10 -(pitch_angle%10))/10)
        small_lines_x = pitch_x + rect_around_pitch_size[0]//2-line_size[0]*0.5//2

        while above_center_y > pitch_y -rect_around_pitch_size[1]//2:
            if above_center_y - line_size[1] > pitch_y -rect_around_pitch_size[1]//2: # if the y of this is in the rect but the text won't be inside we draw only the smaller line
                # longer line
                self.draw_transparent_rect(self.screen, (line_size[0]*0.5, line_size[1]*0.8),100,(255,255,255),(small_lines_x, above_center_y),border_radius=0)
                # angle text
                self.screen.blit(self.font.render(str(round(closest_above_round,1)),True,(255,255,255)),(small_lines_x-self.font.size("100")[0]*1.2, above_center_y - self.font.size("1")[1]//2))
            # shorter line
            self.draw_transparent_rect(self.screen, (line_size[0]*0.25, line_size[1]*0.8),100,(255,255,255),(small_lines_x+line_size[0]*0.5//2-line_size[0]*0.25//2, above_center_y+space_between_lines//2),border_radius=0)
            above_center_y -= space_between_lines
            closest_above_round += 10
        above_center_y = pitch_y - space_between_lines*((10 -(pitch_angle%10))/10) + space_between_lines

        while above_center_y < pitch_y +rect_around_pitch_size[1]//2:
            if above_center_y + line_size[1] < pitch_y +rect_around_pitch_size[1]//2: # if the y of this is in the rect but the text won't be inside we draw only the smaller line
                # longer line
                self.draw_transparent_rect(self.screen, (line_size[0]*0.5, line_size[1]*0.8),100,(255,255,255),(small_lines_x, above_center_y),border_radius=0)
                # angle text
                self.screen.blit(self.font.render(str(round(closest_below_round,1)),True,(255,255,255)),(small_lines_x-self.font.size("100")[0]*1.2, above_center_y - self.font.size("1")[1]//2))
            if above_center_y+space_between_lines//2 < pitch_y +rect_around_pitch_size[1]//2:
                # shorter line
                self.draw_transparent_rect(self.screen, (line_size[0]*0.25, line_size[1]*0.8),100,(255,255,255),(small_lines_x+line_size[0]*0.5//2-line_size[0]*0.25//2, above_center_y+space_between_lines//2),border_radius=0)
            above_center_y += space_between_lines
            closest_below_round -= 10
        
        # green line in the middle
        pygame.draw.rect(self.screen, (33, 252, 147), [pitch_x + rect_around_pitch_size[0]//2-line_size[0]//2, pitch_y, line_size[0], line_size[1]], border_radius=5)
        
        # placing the value of it too
        self.screen.blit(self.medium_font.render(str(round(pitch_angle,1)),True,(255,255,255)),(pitch_x , pitch_y - self.medium_font.size("1")[1]//2))
        
        # roll image showing
        rotated_roll_img = pygame.transform.rotate(self.images["roll"], round(-self.parameters["attitude_roll"],1)) # doing minus the angle because pygame rotates to the left side when positive and we need to the right side when positive, round(num,1) round to one number after the decimal point
        roll_x = pitch_x + rect_around_pitch_size[0]*1.1 + self.images["roll"].get_width()//2 - rotated_roll_img.get_width()//2 # on the right side of the pitch angle representation
        roll_y = pitch_y - rotated_roll_img.get_height()//2 
        self.screen.blit(rotated_roll_img,(roll_x,roll_y))
        self.screen.blit(self.images["pointer above roll"], 
                         (pitch_x + rect_around_pitch_size[0]*1.1 + self.images["roll"].get_width()//2 - self.images["pointer above roll"].get_width()//2,
                           pitch_y - self.images["roll"].get_height()//2 -self.images["pointer above roll"].get_height()//3
                           ))
        
        # below roll text
        self.screen.blit(self.medium_font.render(str(round(self.parameters["attitude_roll"],1)),True, (255,255,255)), 
                         (pitch_x + rect_around_pitch_size[0]*1.1 + self.images["roll"].get_width()//2 - self.medium_font.size(str(round(self.parameters["attitude_roll"],1)))[0]//2, 
                          roll_y + rotated_roll_img.get_height()//2 + self.images["roll"].get_height()//2))
        
        # above roll text
        self.screen.blit(self.medium_font.render("Attitude Roll",True, (255,255,255)), 
                    (pitch_x + rect_around_pitch_size[0]*1.1 + self.images["roll"].get_width()//2 - self.medium_font.size("Attitude Roll")[0]//2,
                    pitch_y - self.images["roll"].get_height()//2 -self.images["pointer above roll"].get_height()//3 - self.medium_font.size("A")[1]
                    ))
        
        # compass image showing
        rotated_compass = pygame.transform.rotate(self.images["compass"], round(self.parameters["compass"],1))
        compass_x = pitch_x + self.images["roll"].get_width()*2 + self.images["compass"].get_width()//2 - rotated_compass.get_width()//2 # on the right side of the roll angle representation
        compass_y = roll_y + rotated_roll_img.get_height()//2 - rotated_compass.get_height()//2  #self.screen.get_height()//2 - rotated_compass.get_height()//2
        self.screen.blit(rotated_compass,(compass_x,compass_y))
        
        self.screen.blit(self.images["pointer"],
                         (pitch_x + self.images["roll"].get_width()*2 + self.images["compass"].get_width()//2 - self.images["pointer"].get_width()//2,
                          roll_y + rotated_roll_img.get_height()//2 - self.images["compass"].get_height()//2 - self.images["pointer"].get_height()
                          ))
        # below compass text
        self.screen.blit(self.medium_font.render("Compass:"+str(round(self.parameters["compass"],1)),True, (255,255,255)), 
                         (pitch_x + self.images["roll"].get_width()*2 + self.images["compass"].get_width()//2 - self.medium_font.size("Compass:"+str(round(self.parameters["compass"],1)))[0]//2, 
                          roll_y + rotated_roll_img.get_height()//2 + self.images["compass"].get_height()//2))
        
        self.screen.blit(self.medium_font.render("Heading:"+str(round(self.parameters["heading"],1)),True, (255,255,255)), 
                         (pitch_x + self.images["roll"].get_width()*2 + self.images["compass"].get_width()//2 - self.medium_font.size("Heading:"+str(round(self.parameters["heading"],1)))[0]//2, 
                          roll_y + rotated_roll_img.get_height()//2 + self.images["compass"].get_height()//2 + self.medium_font.size("C")[1]))
        # above compass text
        self.screen.blit(self.medium_font.render("Compass",True, (255,255,255)), 
                         (pitch_x + self.images["roll"].get_width()*2 + self.images["compass"].get_width()//2 - self.medium_font.size("Compass")[0]//2,
                          roll_y + rotated_roll_img.get_height()//2 - self.images["compass"].get_height()//2 - self.images["pointer"].get_height()*2
                          ))

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
        full_msg = conn.recv(8192).decode() # gets the message from the server   need to be something like this for example "LOGIN           |0009|aaaa#bbbb"
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


def D1_func(parameters_dict, display_num):
    D1_ui = D1("FUI",display_num)
    # update the class parameters
    D1_ui.parameters = parameters_dict

    print("Connected to the server: [SERVER]"+str(SERVER_IP)+":"+str(SERVER_PORT))

    running = True
    while running:
        D1_ui.receive_parameters()
        D1_ui.draw()

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
    D1_func(parameters, 0)
