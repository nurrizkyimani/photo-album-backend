from base64 import encode
from PIL import Image
from google.cloud import storage, firestore, pubsub_v1
from fastapi import FastAPI, status
import json
import io
import uuid
from model import Photo
from urllib.request import urlopen


db = firestore.Client(project="genuine-space-349906")
app = FastAPI()
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

# Photos Model


@app.get('/make_photo_edit')
async def make_photo_edit():

    # get the docs, in this example is the doc with id
    doc_ref = db.collection(u"photos").document("gpeGwKKB2siJWssDQGko")
    real_doc = doc_ref.get()

    real_doc_dict = {"id": real_doc.id, **real_doc.to_dict()}

    # send the data into google pubsub
    project_id = "genuine-space-349906"
    topic_name = "photo_edit"

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    json_ex = json.dumps(real_doc_dict, indent=2).encode('utf-8')
    publisher.publish(topic_path, json_ex)

    return {
        "success": "true",
        "data": real_doc_dict,
    }


@app.get("/upload_photo", status_code=status.HTTP_201_CREATED)
async def upload_photo():
    """ Upload photo to the gcp bucket """
    bucket_name = "photoalbumsppl"
    source_file_name = "test_img_aot.jpg"
    destination_blob_name = "photos/{}".format(source_file_name)

    # call client bucket gcp
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # testing data
    name = "test_img_aot"
    photo_url = "https://storage.googleapis.com/photoalbumsppl/photos/test_img_aot.jpg.jpg"

    new_photo = Photo(url=photo_url,
                      vote=0,
                      thumbnail_url=photo_url,
                      square_url=photo_url,
                      userid='23123123',
                      name=name)

    # add to firestore
    doc_ref = db.collection(u"photos").document()
    doc_ref.set({
        u"url": new_photo.url,
        u"vote": new_photo.vote,
        u"thumbnail_url": new_photo.thumbnail_url,
        u"square_url": new_photo.square_url,
        u"userid": new_photo.userid,
        u"name": new_photo.name,
    })

    return {"id": doc_ref.id, **new_photo.dict()}

# upvote photo route


@app.get("/upvote", status_code=status.HTTP_202_ACCEPTED)
async def upvote_photo():

    # get the id of the photo
    doc_ref = db.collection(u"photos").document("gpeGwKKB2siJWssDQGko")
    # add the upvoote of the photo
    res = doc_ref.update({"vote": firestore.Increment(1)})

    # return success
    return {
        "message": "upvote success",
        "data": res,
    }

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


@app.get('/all_photos', status_code=status.HTTP_200_OK)
async def all_photos():

    # get all photos

    result = db.collection(u"photos").get()
    pat_l = []
    for doc in result:
        pat_l.append({"id": doc.id, **doc.to_dict()})

    return {
        "status": "success",
        "data": pat_l}


# resize the photo with the single click
@app.get('/photo_resize')
async def photo_resize():

    example_id_photo = "gpeGwKKB2siJWssDQGko"
    dest_resize_id = "{}.jpeg".format(uuid.uuid1())

    doc_ref = db.collection(u"photos").document(example_id_photo)
    doc_dict = doc_ref.get().to_dict()

    image = Image.open(urlopen(doc_dict["url"]))
    image.thumbnail((150, 150))

    # save the image to byte array
    bs = io.BytesIO()
    image.save(bs, "jpeg")

    # upload to gcp bucket.
    bucket_name = "photoalbumsppl"

    destination_blob_name = "resizes/{}".format(dest_resize_id)

    # call client bucket gcp
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # add photo to bucket
    blob.upload_from_string(bs.getvalue(), content_type="image/jpeg")

    # get the doc, in this example is the doc with id
    doc_ref = db.collection(u"photos").document(example_id_photo)

    # create the url for the thumbnail
    photo_url = "https://storage.googleapis.com/photoalbumsppl/resizes/{}".format(
        dest_resize_id)

    # update the database with the new thumbnail
    doc_ref.update({"square_url": photo_url})

    return {"status": "success", "message": "Photo Resize"}
