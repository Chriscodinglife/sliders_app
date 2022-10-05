#!/Library/ManagedFrameworks/Python/Python3.framework/Versions/Current/bin/python3

'''
              .c:.
          ....dNO,
       .cxxxxOXO'
      .k0l...,dKo.
      ;Kk.    ;Kk.
      .l0xc::lOO:
        'lKNNO:.
       .:dKNXOl;.
     .l0kl:;;:oOO:
    .oXd.      'OK;
    .xX:       .dNl
     cKO,     .c0O,
     .;xOxooodkOo'
        .;ccc:,.

This script is the front end for the Google Slides New Hire Onboarding app.
This is built upon Tkinter.

'''

import os
import sys
import json
import AppKit
import requests
import webbrowser
import tkinter.ttk
import tkinter as tk
from tkinter import * 
from tkinter.ttk import *
from Cocoa import NSRunningApplication, NSApplicationActivateIgnoringOtherApps


class Sliderama:
    
    def __init__(self):
        
        '''
        Initialize the Tkinter app with the following attributes:
        '''
        
        # Change the flag to True to test locally
        self.troubleshoot_mode = True
        
        # Set some names for colors to use later
        self.black_color = '#000000'
        self.white_color = '#ffffff'
        
        #### MAIN WINDOW ####
        # Create the main window
        self.master_window = tk.Tk()
        
        # Check for sysargs to determine if we are running locally or not
        if self.troubleshoot_mode:
            self.welcome_text = 'Welcome'
            self.backend_url = 'http://localhost:8000'
        else:
            if sys.argv[4]:
                # Set the backend url
                self.backend_url = sys.argv[4]
                # Set the welcome text
                self.welcome_text = sys.argv[5]
            
        self.master_window.title(self.welcome_text)
        all_bundles = AppKit.NSBundle.allBundles()
        for bundle in all_bundles:
            info = bundle.infoDictionary()
            info['CFBundleName'] = self.welcome_text
            info['CFBundleDisplayName'] = self.welcome_text
        
        # Start out with some generic slide info
        self.starting_slide = 0
        self.length_of_slides = 10
        self.ending_slide = self.length_of_slides - 1
        
        # Get the size of the main screen of the user
        self.screen_width = self.master_window.winfo_screenwidth()
        self.screen_height = self.master_window.winfo_screenheight()
        
        # Set the base size of the main window
        self.set_window_width = 1280
        self.set_window_height = 720
        
        self.master_window.configure(width=f"{self.set_window_width}", 
                                     height=f"{self.set_window_height}")
        self.master_window.resizable(True, True)
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
        self.progbar_x_pos = self.window_width_middle
        self.progbar_y_pos = self.window_height - self.progbar_y_adjust

        self.style = tkinter.ttk.Style()
        self.style.theme_use('alt')
        self.style.configure("green.Horizontal.TProgressbar", thickness=5)
        self.progbar = tkinter.ttk.Progressbar(self.master_window)
        self.progbar.configure(length=f"{self.progbar_length}",
                               maximum=self.ending_slide,
                               orient='horizontal',
                               mode='determinate',
                               value=self.starting_slide)
        self.progbar.place(x=self.progbar_x_pos,
                           y=self.progbar_y_pos,
                           anchor='center')
        
        
        #### NAV BUTTONS ####
        self.nav_button_x_adjust = 130
        self.nav_button_y_adjust = 60
        self.back_text = 'Back'
        self.close_text = 'Close'
        self.next_text = 'Next'
        self.finish_text = 'Finish'
        self.default_button_text = 'Button'
        self.button_width = 8
        self.default = 'active'
        
        self.back_button_x_pos = self.window_width_middle - self.nav_button_x_adjust
        self.back_button_y_pos = self.window_height - self.nav_button_y_adjust
        
        self.next_button_x_pos = self.window_width_middle + self.nav_button_x_adjust
        self.next_button_y_pos = self.window_height - self.nav_button_y_adjust
        
        self.back_button = tk.Button(self.master_window)
        self.back_button.configure(text=self.back_text,
                                   highlightbackground=self.black_color,
                                   width=self.button_width,
                                   command=self.close_command)
        self.back_button.place(x=self.back_button_x_pos,
                               y=self.back_button_y_pos,
                               anchor="center")
        
        self.next_button = tk.Button(self.master_window)
        self.next_button.configure(default=self.default,
                                   text=self.next_text,
                                   highlightbackground=self.black_color,
                                   width=self.button_width,
                                   command=self.next_button_command)
        self.next_button.place(x=self.next_button_x_pos,
                               y=self.next_button_y_pos,
                               anchor="center")
            
        #### ACTION BUTTON ####
        self.action_button_y_adjust = 170
        self.action_button_x_pos = self.window_width_middle
        self.action_button_y_pos = self.window_height - self.action_button_y_adjust
        
        self.action_button = tk.Button(self.master_window)
        self.action_button.configure(default=self.default,
                                     text=self.default_button_text)
        self.action_button.place(x=self.action_button_x_pos,
                                 y=self.action_button_y_pos,
                                 anchor="center")
        self.action_button.place_forget()
       
            
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
            return self.slides.json()
        
        
    def close_command(self):
        '''
        Close the application
        '''
        self.master_window.quit()
        
    
    def next_button_command(self):
        '''
        Advance to the next slide
        '''
        pass
    

    def run(self):
        '''
        Run some checks before starting the application
        '''
        self.length_of_slides = self.get_length_of_slides()
        

def main():
    '''Run the app'''
    app = Sliderama()
    app.run()
    app.master_window.mainloop()
    
    

if __name__ == '__main__':
    main()