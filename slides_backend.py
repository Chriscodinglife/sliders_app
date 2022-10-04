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
        self.service = None
        self.image_dir = "images"
        
        
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
        if not os.path.exists(self.image_dir):
            try:      
                os.mkdir(self.image_dir)
            except OSError as error:
                print(error)
        else:
            files = glob.glob(f"{self.image_dir}/*")
            for file in files:
                os.remove(file)
    
    
    def set_service(self):
        '''
        Return the service for the Google Slides API
        '''
        self.service = build('slides', 'v1', credentials=self.creds)
        
        return self.service
        
        
    
    
    def get_presentation_slides(self):
        '''
        Return the slides of the presentation
        '''
        
        self.set_service = self.set_service()
        
        try:
            presentation = self.service.presentations().get(presentationId=self.presentation_id).execute()
            slides = presentation.get('slides')
        except HttpError as error:
            print(error)
        
        return slides
    
    
    def download_images(self):
        '''
        Download the images from the slides
        '''
        
        slides = self.get_presentation_slides()
        
        for i, slide in enumerate(slides):
            
            object_id = slide.get("objectId")
            slide_image = self.service.presentations().pages().getThumbnail(
                            presentationId=self.presentation_id, 
                            pageObjectId=object_id,
                            thumbnailProperties_thumbnailSize='LARGE'
                            ).execute()
            content_url = slide_image['contentUrl']
            
            image_download = requests.get(content_url)
            
            if image_download.status_code == 200:
                with open(f"{self.image_dir}/image_{i}.png", 'wb') as output_image:
                    output_image.write(image_download.content)
                    
    
    def get_notes(self):
        '''
        Return the notes from the slides
        '''
        
        slides = self.get_presentation_slides()
        
        notes = []
        
        for slide in slides:
            notes.append(slide.get("notesPage").get("notesProperties").get("notes"))
            
        return notes