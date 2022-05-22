

# summarization function for the photo
from fastapi import UploadFile
from google.cloud import storage, firestore, pubsub_v1
from model import Photo
import json
import io
import uuid
from urllib.request import urlopen
from PIL import Image
from base64 import encode

db = firestore.Client(project="genuine-space-349906")


def summarization(userid):
    # get the docs, in this example is the doc with id
    doc_ref = db.collection(u"photos").where(
        u"userid",
        u"==",
        userid)

    pht_list = []
    real_doc = doc_ref.get()
    for doc in real_doc:
        pht_list.append(doc.id)

    doc_ref_sum = db.collection(u"summarizations").where(
        u"userid",
        u"==",
        userid).get().exi

    d = doc_ref_sum.get()

    doc_is_exist = False

    for doc in d:
        if doc['userid'] == userid:
            doc_is_exist = True
            break

    if doc_is_exist == True:
        # update the data into firestore
        doc_ref = db.collection(u"summarizations").document(
            "xLcM5cykfr5tp67Lib2M")
        doc_ref.update({"top10all": pht_list})
    else:
        # add the data into firestore
        doc_ref = db.collection(u"summarizations").document()
        doc_ref.set({"userid": userid, "top10all": pht_list})

    return {
        "message": "success",
        "data": pht_list,
    }


# resize photo for 1:1 by the user request


def resize_photo(photo_id):
    if photo_id == None:
        photo_id = "gpeGwKKB2siJWssDQGko"

    dest_resize_id = "{}.jpeg".format(uuid.uuid1())

    doc_ref = db.collection(u"photos").document(photo_id)
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
    doc_ref = db.collection(u"photos").document(photo_id)

    # create the url for the thumbnail
    photo_url = "https://storage.googleapis.com/photoalbumsppl/resizes/{}".format(
        dest_resize_id)

    # update the database with the new thumbnail
    doc_ref.update({"square_url": photo_url})

    return {"status": "success", "message": "Photo Resize"}

# automatically creating thumbnail


def upvote_downvote(incr_vote, photo_id):
    doc_ref = db.collection(u"photos").document(photo_id)

    # update the database with the new thumbnail
    res_json = doc_ref.update({"vote": firestore.Increment(incr_vote)})

    return {"status": "success",
            "message": "Vote updated",
            "data": res_json
            }


def thumbnail_photo_producer(photo_id: int):
    # get the docs, in this example is the doc with id
    doc_ref = db.collection(u"photos").document(photo_id)
    real_doc = doc_ref.get()

    real_doc_dict = {"id": real_doc.id, **real_doc.to_dict()}

    # send the data into google pubsub
    project_id = "genuine-space-349906"
    topic_name = "photo_edit"

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    json_ex = json.dumps(real_doc_dict, indent=2).encode('utf-8')
    publisher.publish(topic_path, json_ex)

    return real_doc_dict


def upload_photo_view(file: UploadFile, userid="23123123"):
    bucket_name = "photoalbumsppl"
    source_file_name = file.filename
    destination_blob_name = "photos/{}".format(source_file_name)

    # call client bucket gcp
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # testing data
    photo_url = "https://storage.googleapis.com/photoalbumsppl/{}".format(
        destination_blob_name)

    new_photo = Photo(url=photo_url,
                      vote=0,
                      thumbnail_url=photo_url,
                      square_url=photo_url,
                      userid=userid,
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


def get_all_photos():
    result = db.collection(u"photos").get()
    pat_l = []
    for doc in result:
        pat_l.append({"id": doc.id, **doc.to_dict()})

    return {
        "status": "success",
        "data": pat_l}
