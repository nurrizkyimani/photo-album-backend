
from PIL import Image
from google.cloud import pubsub_v1, storage, firestore
import time
import json
import os
import sys
import uuid
import io
from urllib.request import urlopen

# information about the project and topic name
project_id = "genuine-space-349906"
subscription_id = "photo_edit-sub"
timeout = 5.0


arr_list = []

db = firestore.Client(project="genuine-space-349906")


def thumbnail_maker(url_img):

    destination_file_name = "{}.jpeg".format(uuid.uuid1())
    try:
        image = Image.open(urlopen(url_img))
        image.thumbnail((90, 90))

        # make it into jpeg format,

        # image.save("test_3.jpg")

        bs = io.BytesIO()
        image.save(bs, "jpeg")
        # in_mem_file.seek(0)

        # upload to gcp bucket.
        bucket_name = "photoalbumsppl"

        destination_blob_name = "thumbnails/{}".format(destination_file_name)

        # call client bucket gcp
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        # add photo to bucket
        res = blob.upload_from_string(bs.getvalue(), content_type="image/jpeg")

        print("inside res", res)

        return False, destination_file_name

    except IOError:
        print("cannot create thumbnail for", url_img)

        return True, None


def callback(message: pubsub_v1.subscriber.message.Message):
    # print(f"Received {message.data!r}.")

    # get data and decode it from bytestring
    json_res = message.data
    res_json_decode = json.loads(json_res)

    # add to arr list as the result
    # arr_list.append(res_json_decode)
    # print(arr_list)

    failed, thumb_id = thumbnail_maker(res_json_decode['url'])

    if(failed):
        print("failed to create thumbnail")
        return

    print("success thumbnail created")

    # print(res_json_decode)
    doc_ref = db.collection(u"photos").document(res_json_decode['id'])

    photo_url = "https://storage.googleapis.com/photoalbumsppl/thumbnails/{}.jpeg".format(
        thumb_id)

    res_up = doc_ref.update({"thumbnail_url": photo_url})

    print({"status": "success", "res": res_up})

    message.ack()


while True:

    print("===============SUBSCRIBER TURN ON====================")

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        project_id, subscription_id)

    print(f"Listening for messages on {subscription_path}..\n")

    # subcribing and pass the data into the callback
    streaming_pull_future = subscriber.subscribe(
        subscription_path,
        callback=callback
    )

    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull_future.result()

        except TimeoutError:
            # Trigger the shutdown.  # Block until the shutdown is complete.
            streaming_pull_future.cancel()
            streaming_pull_future.result()

    time.sleep(3)
