import os
import glob
import json
import base64
import requests
from PIL import Image
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


load_dotenv()

class Slides:
    
    def __init__(self):
        '''
        Initialize the class with the following attributes:
        '''
        self.creds = None
        self.service = None
        self.image_dir = "images"
        self.output_notes = "notes.json"
        self.output_images = "images.json"
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
                
        self.service = build('slides', 'v1', credentials=self.creds)
        
    
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

    
    def get_presentation_slides(self):
        '''
        Return the slides of the presentation
        '''
        
        try:
            presentation = self.service.presentations().get(presentationId=self.presentation_id).execute()
            slides = presentation.get('slides')
        except HttpError as error:
            print(error)
        
        return slides
    
    
    def print_slides(self):
        '''
        Print the slides. Used for troubleshooting
        '''
        
        slides = self.get_presentation_slides()
        
        for slide in slides:
            print(slide)
    
    
    def download_images(self, slides):
        '''
        Download the images from the slides
        '''
        
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
                    
    
    def get_ordered_images(self):
        '''
        Return the images in order
        '''
        
        files = []
        images = []
        
        for file in os.listdir(self.image_dir):
            files.append(f"{self.image_dir}/{file}")
        
        for file in sorted(files, key=os.path.getmtime):
            images.append(file)
            
        print(images)
    
    
    def resize_images(self, images):
        '''
        Resize the images to 800x600
        '''
        
        base_width = 1102
        for file in images:
            image = Image.open(file)
            width_percent = (base_width/float(image.size[0]))
            height_size = int((float(image.size[1])*float(width_percent)))
            new_image = image.resize((base_width, height_size), Image.ANTIALIAS)
            new_image.save(file)
                
                       
    def export_images(self, images):
        '''
        Export the images to a json file for the frontend
        '''
        
        images = []
        
        for file in images:
            with open(file, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                images.append(encoded_string.decode("utf-8"))
                
        with open(self.output_images, "w") as output_file:
            json.dump(images, output_file)
        
        
    def get_notes(self, slides):
        '''
        Return the notes from the slides
        '''
        
        notes = []
        
        for i, slide in enumerate(slides):
            #notes.append(slide.get("slideProperties").get("notesPage").get("notesProperties").get("speakerNotesObjectId"))
            temp = slide.get("slideProperties").get("notesPage").get("pageElements")
            try:
                notes.append(temp[1]["shape"]["text"]["textElements"][1]['textRun']['content'])
            except KeyError as error:
                notes.append("None")
                
        return notes     
    
    
    def export_notes(self, notes):
        '''
        Export the notes to a json file for the frontend
        '''
        
        with open(self.output_notes, "w") as output_file:
            json.dump(notes, output_file)
            
    
    def run(self):
        '''
        Run the class
        '''
        
        self.get_credentials()
        self.fresh_image_directory()
        slides = self.get_presentation_slides()
        self.download_images(slides)
        images = self.get_ordered_images()
        self.resize_images(images)
        self.export_images(images)
        notes = self.get_notes(slides)
        self.export_notes(notes)
        
        
        
def main():
    '''
    Run the class
    '''
    
    slides = Slides()
    slides.run()
    
    
if __name__ == "__main__":
    main()