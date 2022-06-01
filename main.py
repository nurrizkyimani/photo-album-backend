from base64 import encode

from google.cloud import firestore
from fastapi import Body, Depends, FastAPI, UploadFile, status
from AuthBearer.auth_bearer import JWTBearer
from AuthBearer.auth_handler import signJWT
from model import UserLoginSchema, UserSchema


from view import get_all_photos, resize_photo, summarization, thumbnail_photo_producer, upload_photo_view, upvote_downvote


users = []


def check_user(data: UserLoginSchema):

    doc_exist = db.collection(u"users").where(
        u"email",
        u"==",
        data.email).stream()

    for doc in doc_exist:
        doc_user = doc.to_dict()
        if doc_user["email"] == data.email and doc_user["password"] == data.password:
            return True
    # for user in users:
    #     if user.email == data.email and user.password == data.password:
    #         return True

    return False


db = firestore.Client(project="genuine-space-349906")
app = FastAPI()
# main route


@app.get("/")
async def root():
    return {"message": "Hello World"}

# app user signup


@app.post("/user/signup", tags=["user"])
async def create_user(user: UserSchema = Body(...)):
    # replace with db call, making sure to hash the password first

    # create new user model
    new_user = UserSchema(fullname=user.fullname,
                          email=user.email,
                          password=user.password)

    # fetch if email exist
    doc_exist = db.collection(u"users").where(
        u"email",
        u"==",
        new_user.email).stream()

    doc_is_exist = False

    # loop int the docs if doc exist then doc_is_exist = True
    for doc in doc_exist:
        # print(doc.to_dict())
        if doc.exists:
            doc_is_exist = True
            break

    # if exist , we dotn send access token
    if doc_is_exist:
        return {
            "access_token": None,
            "message": "User already exist"}
    # else we ad into the collection and send to the document
    else:
        doc_ref = db.collection(u"users").document()
        doc_ref.set({
            u'fullname': new_user.fullname,
            u'email': new_user.email,
            u'password': new_user.password,
        })

    return signJWT(user.email)


# app user login
@app.post("/user/login", tags=["user"])
async def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return signJWT(user.email)
    return {
        "access_token": None,
        "error": "Wrong login details!"
    }

# test the bearer


@app.get("/test", dependencies=[Depends(JWTBearer())])
async def test():
    return {"message": "Hello World test bearer"}


# upload photo,
    """
    1. upload photo to the bucket
    2. create thumbnail by sendign it to pubsub as producer
    3. return true and the data itself, the doc dic
    """

# upload photo; DONE;


@app.post("/upload_photo", status_code=status.HTTP_201_CREATED)
async def upload_photo(photofile: UploadFile):

    if not photofile:
        return {"message": "No file sent"}

    print(photofile.filename)

    # upload the file; WORK
    res_up = upload_photo_view(photofile, "user1234testing")

    # producer send to create thumbnail; WORK
    real_doc_dict = thumbnail_photo_producer(res_up['id'])

    return {
        "success": "true",
        "data": real_doc_dict,
    }


# upvote photo route; DONE
@app.get("/upvote/{photo_id}", status_code=status.HTTP_202_ACCEPTED)
async def upvote_photo(photo_id: str):

    if photo_id is None:
        photo_id = "gpeGwKKB2siJWssDQGko"

    res_json = upvote_downvote(1, photo_id)

    return res_json

# dowvote the photo route; DONE


@app.get("/downvote/{photo_id}", status_code=status.HTTP_202_ACCEPTED)
async def downvote_photo(photo_id: str):

    if photo_id is None:
        photo_id = "gpeGwKKB2siJWssDQGko"

    res_json = upvote_downvote(-1, photo_id)

    return res_json

# triggler summary; DONE


@app.get('/trigger_summarizer/{userid_input}')
async def top_10_photo_day(userid_input: str):

    if userid_input is None:
        userid_input = "MsvneGYSHOO0j8HTa6GS"

    res_json = summarization(userid_input)

    return res_json


# view top 10 photo with the highest rating route in day; DONE
@app.get('/top_10_photos/{userid_input}')
async def top_10_photo_day(userid_input):

    # get the user docs from the id;
    doc_ref = db.collection(u"users").document(userid_input)
    real_doc = doc_ref.get()
    doc_user = real_doc.to_dict()

    # from the user doc, we get the id of the summarization, and list all of the id photo
    doc_ref_sum = db.collection(u"summarizations").document(
        doc_user['summarization'])
    doc_ref_dict = doc_ref_sum.get()
    res = doc_ref_dict.to_dict()

    list_fetch_photo = []
    for top in res['top10all']:
        list_fetch_photo.append(top)

    # fetch all the photo from the list of id list
    doc_ref_sum = db.collection(u"photos").where(
        u'__name__', u'in', list_fetch_photo).stream()

    list_res_photo = []
    for d in doc_ref_sum:
        list_res_photo.append(d.to_dict())

    # return the status and the data
    return {"status": "success", "data": list_res_photo}

# view all photos from original, thumbnail and 1:1 resultion:


@app.get('/all_photos', status_code=status.HTTP_200_OK)
async def all_photos():
    res_json = get_all_photos()

    return res_json


# resize the photo with the single click, manual; DONE
@app.get("/photo_resize/{photo_id}")
async def photo_resize(photo_id):
    res_json = resize_photo(photo_id)
    return res_json


# view top 10 photo with the highest rating route in day; DONE
@app.get('/get_photo_by_id/{photo_id}')
async def top_10_photo_day(photo_id):

    doc_ref = db.collection(u"photos").document(photo_id)
    real_doc = doc_ref.get()
    real_doc_dict = {"id": real_doc.id, **real_doc.to_dict()}

    return {"status": "success", "data": real_doc_dict}
