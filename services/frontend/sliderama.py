#!/Library/ManagedFrameworks/Python/Python3.framework/Versions/Current/bin/python3

'''

This script is the front end for the sliders API.
This is built upon Tkinter.

'''

import os
import sys
import json
import getpass
import requests
import subprocess
import webbrowser
import tkinter.ttk
import tkinter as tk
from tkinter import * 
from tkinter.ttk import *
from subprocess import Popen
from multiprocessing import Process, Queue
from Cocoa import NSRunningApplication, NSApplicationActivateIgnoringOtherApps


class Sliderama:
    
    def __init__(self):
        
        '''
        Initialize the Tkinter app with the following attributes:
        '''
        
        #### RUN CONFIGS ####
        # Use this section to configure settings for running the app in different environments
        
        # Get current process and user info
        self.parent_command = os.getpid()
        self.jamf_binary = '/usr/local/jamf/bin/jamf'
        self.current_user = None
        
        # Change the Troubleshoot Mode flag to True to test locally
        # Set to False if running in production/JAMF
        self.troubleshoot_mode = True
        if self.troubleshoot_mode:
            # Set the values below to test locally
            self.welcome_text = 'Welcome'
            self.backend_url = 'https://8bda-2603-7000-e340-900f-8c7d-5a3b-a097-ef0e.ngrok.io'
            self.current_user = getpass.getuser()
            self.app_icon_path = ""
        else:
            if sys.argv[3]:
                # Set the current user based on JAMF
                self.current_user = sys.argv[3]
            if sys.argv[4]:
                # Set the backend url
                self.backend_url = sys.argv[4]
            if sys.argv[5]:
                # Set the welcome text
                self.welcome_text = sys.argv[5]
            if sys.argv[6]:
                # Set the app icon path
                self.app_icon_path = sys.argv[6]
            else:
                self.app_icon_path = f"/Users/{self.current_user}/Library/Application Support/com.jamfsoftware.selfservice.mac/Documents/Images/brandingimage.png"
            if not self.check_back_end_status():
                print("Backend is not running")
                sys.exit(1)
                
        #### MAIN WINDOW ####
        # Create the main window
        self.master_window = tk.Tk()
        
        # Create the app icon if available
        if os.path.exists(self.app_icon_path):
            self.app_icon = tk.PhotoImage(file=self.app_icon_path)
            self.master_window.call('wm', 'iconphoto', self.master_window._w, self.app_icon)
        
        # Set some names for colors to use later
        self.black_color = '#000000'
        self.white_color = '#ffffff'
    
        self.master_window.title(self.welcome_text)
        
        # Start out with some generic slide info
        self.starting_slide = 0
        self.length_of_slides = 10
        self.ending_slide = self.length_of_slides - 1
        
        # Get the size of the main screen of the user
        self.screen_width = self.master_window.winfo_screenwidth()
        self.screen_height = self.master_window.winfo_screenheight()
        
        # Set the base size of the main window
        self.set_window_width = 1280
        self.set_window_height = 820
        
        self.master_window.configure(width=f"{self.set_window_width}", 
                                     height=f"{self.set_window_height}")
        self.master_window.resizable(False, False)
        self.master_window.update()
        
        # Get the size of the main window
        self.window_width = self.master_window.winfo_width()
        self.window_height = self.master_window.winfo_height()
        
        # Get the middle of the main window and screen
        self.window_width_middle = self.window_width / 2
        self.window_height_middle = self.window_height / 2
        self.screen_width_middle = self.screen_width / 2
        self.screen_height_middle = self.screen_height / 2
        
        # Set the position of the main window
        self.window_x_pos = int(self.screen_width_middle - self.window_width_middle)
        self.window_y_pos = int(self.screen_height_middle - self.window_height_middle)
        
        self.master_window.geometry(f"+{self.window_x_pos}+{self.window_y_pos}")
        
        # Bring the window to the front and in focus
        self.master_window_process = NSRunningApplication.runningApplicationWithProcessIdentifier_(os.getpid())
        self.master_window_process.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
        
        # Configure the Columns
        self.master_window.columnconfigure(2, minsize=200)
        self.master_window.columnconfigure(3, minsize=200)
        self.master_window.columnconfigure(4, minsize=200)
        
        #### MAIN CANVAS ####
        self.row = '0'
        self.rowspan = '6'
        self.column = '0'
        self.columnspan = '7'
        
        self.black_canvas = tk.Canvas(self.master_window)
        self.black_canvas.configure(background=self.black_color,
                                    width=self.window_width,
                                    height=self.window_height)
        self.black_canvas.grid(row=self.row, 
                               rowspan=self.rowspan, 
                               column=self.column, 
                               columnspan=self.columnspan)
        
        #### TOP IMAGE CANVAS ####
        self.top_canvas_y_adjust = 100
        self.top_canvas = tk.Canvas(self.master_window)
        self.top_canvas.configure(background=self.white_color,
                                  width=self.window_width,
                                  height=str(self.window_height - self.top_canvas_y_adjust),
                                  highlightbackground=self.white_color)
        self.top_canvas.grid(row=self.row,
                             rowspan=self.rowspan,
                             column=self.column,
                             columnspan=self.columnspan,
                             sticky='n')
        
        #### PROGRESS BAR ####
        self.progbar_y_adjust = 125
        self.progbar_length = 600
        self.progbar_thickness = 5
        self.progbar_x_pos = self.window_width_middle
        self.progbar_y_pos = self.window_height - self.progbar_y_adjust
        self.anchor = 'center'

        self.style = tkinter.ttk.Style()
        self.style.theme_use('alt')
        self.style.configure("green.Horizontal.TProgressbar", thickness=self.progbar_thickness)
        self.progbar = tkinter.ttk.Progressbar(self.master_window)
        self.progbar.configure(length=f"{self.progbar_length}",
                               maximum=self.ending_slide,
                               orient='horizontal',
                               mode='determinate',
                               value=self.starting_slide,
                               style="green.Horizontal.TProgressbar")
        self.progbar.place(x=self.progbar_x_pos,
                           y=self.progbar_y_pos,
                           anchor=self.anchor)
         
        #### NAV BUTTONS ####
        self.nav_button_x_adjust = 130
        self.nav_button_y_adjust = 60
        self.back_text = 'Back'
        self.close_text = 'Close'
        self.next_text = 'Next'
        self.finish_text = 'Finish'
        self.action_button_text = 'Complete This Task'
        self.button_width = 8
        self.default = 'active'
        
        self.back_button_x_pos = self.window_width_middle - self.nav_button_x_adjust
        self.back_button_y_pos = self.window_height - self.nav_button_y_adjust
        
        self.next_button_x_pos = self.window_width_middle + self.nav_button_x_adjust
        self.next_button_y_pos = self.window_height - self.nav_button_y_adjust
        
        self.back_button = tk.Button(self.master_window)
        self.back_button.configure(text=self.close_text,
                                   highlightbackground=self.black_color,
                                   width=self.button_width,
                                   command=self.close_command)
        self.back_button.place(x=self.back_button_x_pos,
                               y=self.back_button_y_pos,
                               anchor=self.anchor)
        
        self.next_button = tk.Button(self.master_window)
        self.next_button.configure(default=self.default,
                                   text=self.next_text,
                                   highlightbackground=self.black_color,
                                   width=self.button_width,
                                   command=self.next_button_command)
        self.next_button.place(x=self.next_button_x_pos,
                               y=self.next_button_y_pos,
                               anchor=self.anchor)
            
        #### ACTION BUTTON ####
        self.action_button_y_adjust = 170
        self.action_button_x_pos = self.window_width_middle
        self.action_button_y_pos = self.window_height - self.action_button_y_adjust
        
        self.action_button = tk.Button(self.master_window)
        self.action_button.configure(default=self.default,
                                     text=self.action_button_text)
        self.action_button.place(x=self.action_button_x_pos,
                                 y=self.action_button_y_pos,
                                 anchor=self.anchor)
        self.action_button.place_forget()
        
        self.check_list = ['http://', 'https://', 'jamfselfservice://', 'chrome-extension://', '/Applications', '/System']
        self.web_list = ['http://', 'https://', 'jamfselfservice://', 'chrome-extension://']
        self.app_list = ['/Applications', '/System']
        self.note = ""
       
            
    def check_back_end_status(self):
        '''
        Check the backend to ensure the server is running
        '''
        self.backend_status = requests.get(f"{self.backend_url}/ping")
        if self.backend_status.status_code == 200:
            return True
        else:
            return False


    def get_length_of_slides(self):
        '''
        Return the number of slides from the backend
        '''
        self.slides = requests.get(f"{self.backend_url}/len")
        if self.slides.status_code == 200:
            self.length_of_slides = self.slides.json()['total_slides']
            self.progbar.configure(maximum=self.length_of_slides - 1)
            self.ending_slide = self.length_of_slides - 1
            
    
    def add_to_progbar(self):
        '''
        Increment the progress bar by 1 and return the current value
        '''
        
        self.progbar['value'] += 1
        
        if self.progbar['value'] >= self.ending_slide:
            self.progbar['value'] = self.ending_slide
            
    
    def set_back_button(self):
        '''
        Make the back button visible
        '''
        self.back_button.configure(text=self.back_text,
                                    command=self.back_button_command)
        self.back_button.place(x=self.back_button_x_pos,
                                y=self.back_button_y_pos,
                                anchor=self.anchor)
        
        
    def set_close_button(self):
        '''
        Make the close button visible
        '''
        self.back_button.configure(text=self.close_text,
                                   command=self.close_command)
        
        
    def set_finish_button(self):
        '''
        Make the finish button visible and the back button dissappear
        '''
        self.back_button.place_forget()
        self.next_button.configure(text=self.finish_text,
                                   command=self.close_command)
        self.next_button.place(x=self.window_width_middle,
                               y=self.next_button_y_pos,
                               anchor=self.anchor)
            
            
    def close_command(self):
        '''
        Close the application
        '''
        self.master_window.quit()
        
        
    def subtract_from_progbar(self):
        '''
        Decrement the progress bar by 1 and return the current value
        '''
        
        self.progbar['value'] -= 1
        
        if self.progbar['value'] <= self.starting_slide:
            self.progbar['value'] = self.starting_slide

    
    def next_button_command(self):
        '''
        Command for the next button to increment the progress bar
        '''
        
        self.add_to_progbar()
        self.current_slide = self.progbar['value']
        
        self.set_slide(self.current_slide)
        self.set_note(self.current_slide)
        
        if self.current_slide >= 1 and self.current_slide < self.ending_slide:
            self.set_back_button()
        elif self.current_slide == self.ending_slide:
            self.set_finish_button()

        self.master_window.update()
        
        
    def back_button_command(self):
        '''
        Command for the back button to decrement the progress bar
        '''
        self.subtract_from_progbar()
        self.current_slide = self.progbar['value']
        
        self.set_slide(self.current_slide)
        self.set_note(self.current_slide)
        
        if self.current_slide == self.starting_slide:
            self.set_close_button()
            
        self.master_window.update()     
            
    
    def get_image(self, slide_number):
        '''
        Return the image data from the backend
        '''
        self.image_response = requests.get(f"{self.backend_url}/images/{slide_number}")
        if self.image_response.status_code == 200:
            self.image = self.image_response.json()['image']
            return self.image
        
    
    def get_note(self, slide_number):
        '''
        Return the note data from the backend
        '''
        self.note_response = requests.get(f"{self.backend_url}/notes/{slide_number}")
        if self.note_response.status_code == 200:
            self.note = self.note_response.json()['note']
            return self.note
        
        
    def set_slide(self, slide_number):
        '''
        Set the slide image
        '''
        self.image = self.get_image(slide_number)
        
        self.slide_image = tk.PhotoImage(data=self.image)
        self.top_canvas.create_image(0, 0, image=self.slide_image, anchor='nw')
            
        self.master_window.update()
        
        
    def action_button_command(self):
        '''
        Set the action button command
        '''
        self.chrome_exe = 'open -a /Applications/Google\ Chrome.app %s'
        self.chrome_path = '/Applications/Google Chrome.app'
        
        if any(call in self.note for call in self.web_list):
            if os.path.exists(self.chrome_path):
                webbrowser.get(self.chrome_exe).open(self.note)
        elif any(call in self.note for call in self.app_list):
            Popen(['open', self.note])
            
        
    def set_note(self, slide_number):
        '''
        Set the note text
        '''
        self.note = self.get_note(slide_number)
        
        if self.note == "None":
            self.action_button.place_forget()
        
        elif any(call in self.note for call in self.check_list):
            self.action_button.place(x=self.action_button_x_pos,
                        y=self.action_button_y_pos,
                        anchor=self.anchor)
            self.action_button.configure(command=self.action_button_command)
        else:
            self.action_button.place_forget()
            
        self.master_window.update()
    

    def run(self):
        '''
        Run the Sliderama App
        '''
        self.get_length_of_slides()
        self.set_slide(0)
        self.set_note(0)
        self.master_window.mainloop()
        
    
def run_app():
    '''Run the app'''
    app = Sliderama()
    app.run()
    
    
if __name__ == '__main__':
    child_process = Process(target=run_app)
    child_process.daemon = False
    child_process.start()
    exit()
