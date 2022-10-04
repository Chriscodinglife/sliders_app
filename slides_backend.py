import os
import glob
import json
import base64
import requests
from PIL import Image
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

# I want to do two things:
# 1. Download the images from the Google Slides presentation
# 2. Grab the text from the Google Slides presentation notes area
# 3. With a specific endpoint, I want to update the images and text in the database


class Slides:
    
    def __init__(self):
        '''
        Initialize the class with the following attributes:
        '''
        self.creds = None
        self.scopes = [f"{os.getenv('SCOPES')}"]
        self.presentation_id = os.getenv('PRESENTATION_ID')
        
        
    def get_credentials(self):
        '''
        Set the credentials for the Google Slides API
        '''
        
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', self.scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.scopes)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        
    
    def fresh_image_directory(self):
        '''
        Create a local image folder for storing images
        '''
        image_directory = 'images'
        if not os.path.exists(image_directory):
            try:      
                os.mkdir(image_directory)
            except OSError as error:
                print(error)
        else:
            files = glob.glob(f"{image_directory}/*")
            for file in files:
                os.remove(file)
                
    
    