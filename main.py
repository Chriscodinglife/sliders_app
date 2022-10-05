from fastapi import FastAPI
from slider import Slides

app = FastAPI()

slider = Slides()

@app.get("/ping", status_code=200)
def ping():
    '''
    Return a generic ping response
    '''
    return {"Hello": "World"}


@app.get("/total_slides", status_code=200)
def total_slides():
    '''
    Return the total number of slides in the presentation
    '''
    slides = slider.get_number_of_slides()
    return {"total_slides": len(slides)}


@app.get("/generate_slides", status_code=200)
def generate_slides():
    '''
    Generate new slides upon request and return a success message
    '''
    slide_status = slider.run()