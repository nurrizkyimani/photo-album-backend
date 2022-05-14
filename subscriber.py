
from google.cloud import pubsub_v1
import time
import json

# information about the project and topic name
project_id = "genuine-space-349906"
subscription_id = "photo_edit-sub"
timeout = 5.0


arr_list = []


def callback(message: pubsub_v1.subscriber.message.Message):
    # print(f"Received {message.data!r}.")

    # get data and decode it from bytestring
    json_res = message.data
    res_json_decode = json.loads(json_res)

    # add to arr list as the result
    arr_list.append(res_json_decode)
    print(arr_list)

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
