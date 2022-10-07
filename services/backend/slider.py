import os
import glob
import json
import base64
import requests
from PIL import Image
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


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
        self.cred_file = os.getenv('CLIENT_SECRET_FILE')
        self.scopes = [f"{os.getenv('SCOPES')}"]
        self.presentation_id = os.getenv('PRESENTATION_ID')
        
        
    def get_credentials(self):
        '''
        Set the credentials for the Google Slides API
        '''
                
        self.credentials = service_account.Credentials.from_service_account_file(self.cred_file)
        self.scoped_credentials = self.credentials.with_scopes(self.scopes)
        self.service = build('slides', 'v1', credentials=self.scoped_credentials)
        
    
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
            self.slides = presentation.get('slides')
        except HttpError as error:
            print(error)
        
        return self.slides
    
    
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
            
        return images
    
    
    def get_number_of_slides(self):
        '''
        Return the number of slides in the presentation
        '''
        
        return len(os.listdir(self.image_dir))
    
    
    def resize_images(self, images):
        '''
        Resize the images to 800x600
        '''
        
        base_width = 1280
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
        
        binary_images = []
        
        for file in images:
            with open(file, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                binary_images.append(encoded_string.decode("utf-8"))
                
        with open(self.output_images, "w") as output_file:
            json.dump(binary_images, output_file)
            
            
    def get_image(self, slide_number):
        '''
        Return the image at a specific slide number
        '''
        
        with open(self.output_images, "r") as input_file:
            images = json.load(input_file)
        
        return images[slide_number]
        
        
    def get_notes(self, slides):
        '''
        Return the notes from the slides
        '''
        
        notes = []
        
        for i, slide in enumerate(slides):
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
            
        
    def get_note(self, slide_number):
        '''
        Return the note for a specific slide
        '''
        
        with open(self.output_notes, "r") as input_file:
            notes = json.load(input_file)
            
        return notes[slide_number].split('\n')[0] 
            
    
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
        
        return 200
        
                
def main():
    '''
    Run the class
    '''
    
    slides = Slides()
    slides.run()
    
    
if __name__ == "__main__":
    main()