from google.cloud import storage
from fastapi import FastAPI
from sqlalchemy import create_engine, Integer, Column, String, ForeignKey, select, inspect
from sqlalchemy.orm import declarative_base, Session

app = FastAPI()

# create a connection between fastapi and gcp bucket
engine = create_engine(
    "postgresql://postgres:Denhaag898!@34.132.87.247:5432/postgres", echo=True, future=True)

# Declare the base

Base = declarative_base()


class Photo(Base):
    __tablename__ = "photosdb"
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    url = Column(String)
    vote = Column(Integer)

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


# create the table
Base.metadata.create_all(engine)

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
    """ Upload photo to the gcp bucket """
    bucket_name = "photoalbumsppl"
    source_file_name = "test_img_aot.jpg"
    destination_blob_name = "photos/{}.jpg".format(source_file_name)

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # blob.upload_from_filename(source_file_name)

    res = "File {} uploaded to {}.".format(
        source_file_name, destination_blob_name)

    # declare_model

    photo_1 = Photo(
        name="test", url="https://storage.googleapis.com/photoalbumsppl/photos/test_img_aot.jpg")

    # post the photo with user data to the gcp sql database
    with Session(engine) as session:
        session.add(photo_1)
        session.commit()

    return {"message": res}

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

    with Session(engine) as session:
        stmt = select(Photo)
        photos_arr = []
        for photo in session.scalars(stmt):
            photos_arr.append(photo.as_dict())

    return {"message": photos_arr}


# resize the photo with the single click
@app.get('photo_resize')
async def photo_resize():
    return {"message": "Photo Resize"}
