from base64 import encode

from google.cloud import firestore
from fastapi import Body, Depends, FastAPI, UploadFile, status
from AuthBearer.auth_bearer import JWTBearer
from AuthBearer.auth_handler import signJWT
from model import UserLoginSchema, UserSchema


from view import get_all_photos, resize_photo, summarization, thumbnail_photo_producer, upload_photo_view, upvote_downvote


users = []


def check_user(data: UserLoginSchema):
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False


db = firestore.Client(project="genuine-space-349906")
app = FastAPI()
# main route


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/user/signup", tags=["user"])
async def create_user(user: UserSchema = Body(...)):
    # replace with db call, making sure to hash the password first
    users.append(user)
    return signJWT(user.email)


@app.post("/user/login", tags=["user"])
async def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return signJWT(user.email)
    return {
        "error": "Wrong login details!"
    }

# test the bearer


@app.post("/test", dependencies=[Depends(JWTBearer())])
async def test():
    return {"message": "Hello World"}


@app.post("/upload_photo", status_code=status.HTTP_201_CREATED)
async def upload_photo(photofile: UploadFile):

    if not photofile:
        return {"message": "No file sent"}

    print(photofile.filename)

    # upload the file
    res_up = upload_photo_view(photofile)

    # producer send
    real_doc_dict = thumbnail_photo_producer(res_up['id'])

    return {
        "success": "true",
        "data": real_doc_dict,
    }


# upvote photo route
@app.get("/upvote/{photo_id}", status_code=status.HTTP_202_ACCEPTED)
async def upvote_photo(photo_id: str):

    if photo_id is None:
        photo_id = "gpeGwKKB2siJWssDQGko"

    res_json = upvote_downvote(1, photo_id)

    return res_json


@app.get("/downvote/{photo_id}", status_code=status.HTTP_202_ACCEPTED)
async def downvote_photo(photo_id: str):

    if photo_id is None:
        photo_id = "gpeGwKKB2siJWssDQGko"

    res_json = upvote_downvote(-1, photo_id)

    return res_json


@app.get('/trigger_summarizer/{userid_input}')
async def top_10_photo_day(userid_input: str):

    if userid_input is None:
        userid_input = "MsvneGYSHOO0j8HTa6GS"

    res_json = summarization(userid_input)

    return res_json


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
    res_json = get_all_photos()

    return res_json


# resize the photo with the single click
@app.get("/photo_resize/{photo_id}")
async def photo_resize(photo_id):
    res_json = resize_photo(photo_id)

    return res_json
