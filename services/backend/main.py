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


@app.get("/len", status_code=200)
def len():
    '''
    Return the total number of slides in the presentation
    '''
    slides = slider.get_number_of_slides()
    return {"total_slides": slides}


@app.post("/generate_slides", status_code=200)
def generate_slides():
    '''
    Generate new slides upon request and return a success message
    '''
    slider.run()
    return {"slide_status": "success"}


@app.get("/generate_test", status_code=200)
def generate_slides():
    '''
    Generate new slides upon request and return a success message
    '''
    slider.run()
    return {"slide_status": "success"}


@app.get("/notes/{slide_number}", status_code=200)
def get_notes(slide_number: int):
    '''
    Return the notes for a given slide
    '''
    note = slider.get_note(slide_number)
    return {"note": note}


@app.get("/images/{slide_number}", status_code=200)
def get_image(slide_number: int):
    '''
    Return the image for a given slide
    '''
    image = slider.get_image(slide_number)
    return {"image": image}