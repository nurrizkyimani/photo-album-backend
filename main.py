from base64 import encode
from PIL import Image
from google.cloud import storage, firestore, pubsub_v1
from fastapi import FastAPI, UploadFile, status
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


@app.post("/upload_photo", status_code=status.HTTP_201_CREATED)
async def upload_photo(file: UploadFile):

    if not file:
        return {"message": "No file sent"}

    print(file.filename)

    bucket_name = "photoalbumsppl"
    source_file_name = file.filename
    destination_blob_name = "photos/{}".format(source_file_name)

    # call client bucket gcp
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # testing data
    name = "test_img_aot"
    photo_url = "https://storage.googleapis.com/photoalbumsppl/{}".format(
        destination_blob_name)

    new_photo = Photo(url=photo_url,
                      vote=0,
                      thumbnail_url=photo_url,
                      square_url=photo_url,
                      userid='23123123',
                      name=source_file_name)

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


@app.get("/downvote", status_code=status.HTTP_202_ACCEPTED)
async def upvote_photo():

    # get the id of the photo
    doc_ref = db.collection(u"photos").document("gpeGwKKB2siJWssDQGko")
    # add the upvoote of the photo
    res = doc_ref.update({"vote": firestore.Increment(-1)})

    # return success
    return {
        "message": "upvote success",
        "data": res,
    }


@app.get('/trigger_summarizer')
async def top_10_photo_day():

    userid_input = 'MsvneGYSHOO0j8HTa6GS'

    doc_ref = db.collection(u"photos").where(
        u"userid",
        u"==",
        userid_input)

    real_doc = doc_ref.get()

    pht_list = []

    for doc in real_doc:
        pht_list.append(doc.id)

    doc_ref = db.collection(u"summarizations").document("xLcM5cykfr5tp67Lib2M")
    doc_ref.update({"top10all": pht_list})

    return {
        "message": "success",
        "data": pht_list,
    }


# view top 10 photo with the highest rating route in day


@app.get('/top_10_photos')
async def top_10_photo_day():

    doc_ref = db.collection(u"photos").document("xLcM5cykfr5tp67Lib2M")
    real_doc = doc_ref.get()
    real_doc_dict = {"id": real_doc.id, **real_doc.to_dict()}

    return {"status": "success", "data": real_doc_dict}

# view all photos from original, thumbnail and 1:1 resultion:


@app.get('/all_photos', status_code=status.HTTP_200_OK)
async def all_photos():

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
