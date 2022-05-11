from fastapi import FastAPI

app = FastAPI()

# create a connection between fastapi and gcp bucket

# main route


@app.get("/")
async def root():
    return {"message": "Hello World"}


# sign up function
@app.post("/signup")
async def signup():
    pass

# sign in function


@app.post("/signin")
async def signin():
    pass

# get user credential


@app.get("/user")
async def user():
    pass

# upload picture route


@app.get("/upload_photo")
async def upload_photo():

    # take the data from the body

    # post into google cloud

    # return a appropriate response

    # add the id of the photo into sql database
    return {"message": "Upload Picture"}

# upvote photo route


@app.get("/upvote")
async def upvote_photo():

    # get the id of the photo

    # add the upvoote of the photo

    # update it into the photo sql database;

    return {"message": "Upload Picture"}

# view top 10 photo with the highest rating route in day


@app.get('/top_10_photo_day')
async def top_10_photo_day():
    return {"message": "Top 10 Photo Day"}

# view top 10 photo with the highest rating route in month


@app.get('/top_10_photo_month')
async def top_10_photo_month():
    return {"message": "Top 10 Photo Month"}

# view top 10 photo with the highest rating route weekly


@app.get('/top_10_photo_week')
async def top_10_photo_week():
    return {"message": "Top 10 Photo Week"}

# view all photos from original, thumbnail and 1:1 resultion:


@app.get('/all_photos')
async def all_photos():

    return {"message": "All Photos"}


# resize the photo with the single click
@app.get('photo_resize')
async def photo_resize():
    return {"message": "Photo Resize"}
