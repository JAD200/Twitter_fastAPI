# Python
import json
from uuid import UUID
from datetime import date
from datetime import datetime
from typing import Optional, List


# Pydantic
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field

# FastAPI
from fastapi import FastAPI
from fastapi import status
from fastapi import HTTPException
from fastapi import Body, Query, Path, Form

app = FastAPI()

# Models

class UserBase(BaseModel):
    user_id: UUID = Field(...)
    email: EmailStr = Field(...)

class UserLogin(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=64
    )

class LoginOut(BaseModel):
    email: EmailStr = Field(...)
    message: str = Field(default="Login Successful!")

class User(UserBase):
    fist_name: str = Field(
        ...,
        min_length=1,
        max_length=50
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50
    )
    birth_date: Optional[date] = Field(default=None)

class UserRegister(User):
    password: str = Field(
    ...,
    min_length=8,
    max_length=64
    )

class Tweet(BaseModel):
    tweet_id: UUID = Field(...)
    content: str = Field(
        ...,
        min_length=1,
        max_length=256
    )
    created_at: datetime = Field(default=datetime.now())
    updated_at: Optional[datetime] = Field(default=None)
    by: User = Field(...)

#* Path operations

##* Users

### Register a user
@app.post(
    path="/signup",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Register a User",
    tags=["Users"]
)
def signup(user: UserRegister = Body(...)):
    """# Signup

    This path operation registers a user in the app

    Parameters:
    - Request body parameter
        - user: register

    Returns:
    - Json with the basic user information:
        - user_id: UUID
        - email: str
        - first_name: str
        - last_name: str
        - birth_date: datetime
    """
    with open('users.json', 'r+', encoding='utf-8') as f:
        results = json.loads(f.read())
        user_dict = user.dict()
        user_dict["user_id"] = str(user_dict["user_id"])
        user_dict["birth_date"] = str(user_dict["birth_date"])
        results.append(user_dict)
        f.seek(0)
        f.write(json.dumps(results))
        return user

### Login a user
@app.post(
    path='/login',
    response_model=LoginOut,
    status_code=status.HTTP_200_OK,
    summary='Login a user',
    tags=['Users']
)
def login(
    email: EmailStr = Form(..., description='User email'),
    password: str = Form(..., description='User account password')
):
    """# User login

    This path operation is the login for an existing user in the app

    Parameters:
    - Request body parameter
        - email: EmailStr
        - password: str

    Returns:
    - Different message with the login information
    """
    with open("users.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
        for user in results:
            if email == user['email'] and password == user['password']:
                return LoginOut(email=email)
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Login Unsuccessful!")


### Show all users
@app.get(
    path='/users',
    response_model=List[User],
    status_code=status.HTTP_200_OK,
    summary='Show all users',
    tags=['Users']
)
def show_all_users():
    """# Show all users

    This path operation shows all users in the app

    Parameters:
        -

    Returns:
    - Json with all the users in the app, with the following keys:
        - user_id: UUID
        - email: str
        - first_name: str
        - last_name: str
        - birth_date: datetime
    """
    with open('users.json', 'r', encoding='utf-8') as f:
        results = json.loads(f.read())
        return results

### Show a user
@app.get(
    path='/users/{user_id}',
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary='Show a user',
    tags=['Users']
)
def show_a_user(
    user_id: str = Path(
        ...,
        title='User ID',
        description='This is the ID of the user to be shown',
        example='3fa85f64-5717-4562-b3fc-2c963f66afa6'
    )
):
    """# Show a user

    This path operation shows a user in the app

    Parameters:
    - user_id: str

    Returns:
    - Json with a user information in the app, with the following keys:
        - user_id: UUID
        - email: str
        - first_name: str
        - last_name: str
        - birth_date: datetime
    """
    with open('users.json', 'r', encoding='utf-8') as f:
        results = json.loads(f.read())
        id = str(user_id)
        for data in results:
            if data["user_id"] == id:
                return data
            else:
                raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"¡This user ID doesn't exists!"
            )

### Delete a user
@app.delete(
    path='/users/{user_id}/delete',
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary='Delete a user',
    tags=['Users']
)
def delete_a_user(
    user_id: str = Path(
        ...,
        title='User ID',
        description='This is the ID of the user to be deleted',
        example='3fa85f64-5717-4562-b3fc-2c963f55afb7'
    ),
):
    """# Delete a user

    This path operation deletes a user in the app

    Parameters:
    - user_id: str

    Returns:
    - Json with deleted user data:
        - user_id: UUID
        - content: str
        - created_at: datetime
        - updated_at: Optional[datetime]
        - by: User
    """
    with open('users.json', 'r+', encoding='utf-8') as f:
        deletion = json.loads(f.read())
        id = str(user_id)
        for data in deletion:
            if data['user_id'] == id:
                deletion.remove(data)
                with open("users.json", "w", encoding="utf-8") as f:
                    f.seek(0)
                    f.write(json.dumps(deletion))
                return data
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="¡This user ID doesn't exist!"
            )

### Update a user
@app.put(
    path='/users/{user_id}/update',
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary='Update a user',
    tags=['Users']
)
def update_a_user(
    user_id: str = Path(
        ...,
        title='User ID',
        description='This is the ID of the user to be deleted',
        example='3fa85f64-5717-4562-b3fc-2c963f66afa6'
    ),
    user: UserRegister = Body(...)
):
    # """# Update user information

    # This path operation updates an existing user information in the app

    # Parameters:
    # - Path body parameters
    #     - user_id: UUID
    #     - user: UserRegister

    # Returns:
    # - Json with the basic user information:
    #     - user_id: UUID
    #     - email: str
    #     - first_name: str
    #     - last_name: str
    #     - birth_date: datetime
    # """
    # with open("users.json", "r+", encoding="utf-8") as f:
    #     user_id = str(user_id)
    #     user_dict = user.dict()
    #     user_dict["user_id"] = str(user_dict["user_id"])
    #     user_dict["birth_date"] = str(user_dict["birth_date"])
    #     with open("users.json", "r+", encoding="utf-8") as f:
    #         results = json.loads(f.read())
    #         for user in results:
    #             if user["user_id"] == user_id:
    #                 results.remove(user)
    #                 results.append(user_dict)
    #                 f.seek(0)
    #                 f.write(json.dumps(results))
    #                 return user
    #         else:
    #             raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             message="¡This user doesn't exist!"
    #             )
    pass


##* Tweets

### Show all tweets
@app.get(
    path='/',
    response_model=List[Tweet],
    status_code=status.HTTP_200_OK,
    summary='Show all tweets',
    tags=['Tweets']
)
def  home():
    """# Show all tweets

    This path operation shows all tweets in the app

    Parameters:
        -

    Returns:
    - Json with all the tweets in the app, with the following keys:
        - tweet_id: UUID
        - content: str
        - created_at: datetime
        - updated_at: Optional[datetime]
        - by: User
    """
    with open('tweets.json', 'r', encoding='utf-8') as f:
        results = json.loads(f.read())
        return results

### Post a tweet
@app.post(
    path="/post",
    response_model=Tweet,
    status_code=status.HTTP_201_CREATED,
    summary="Post a Tweet",
    tags=["Tweets"]
)
def post(tweet: Tweet = Body(...)):
    """# Post a tweet

    This path operation posts a tweet in the app

    Parameters:
    - Request body parameter
        - tweet: Tweet

    Returns:
    - Json with the basic tweet information:
        - tweet_id: UUID
        - content: str
        - created_at: datetime
        - updated_at: Optional[datetime]
        - by: User
    """
    with open('tweets.json', 'r+', encoding='utf-8') as f:
        results = json.loads(f.read())
        tweet_dict = tweet.dict()
        tweet_dict["tweet_id"] = str(tweet_dict["tweet_id"])
        tweet_dict["created_at"] = str(tweet_dict["created_at"])
        tweet_dict["updated_at"] = str(tweet_dict["updated_at"])
        tweet_dict["by"]["user_id"] = str(tweet_dict["by"]["user_id"])
        tweet_dict["by"]["birth_date"] = str(tweet_dict["by"]["birth_date"])
        results.append(tweet_dict)
        f.seek(0)
        f.write(json.dumps(results))
        return tweet

### Show a tweet
@app.get(
    path="/tweets/{tweet_id}",
    status_code=status.HTTP_200_OK,
    summary="Show a Tweet",
    tags=["Tweets"]
)
def show_a_tweet(
    tweet_id: str = Path(
        ...,
        title='Tweet ID',
        description='This is the ID of the tweet to be shown',
        example='3fa85f64-5717-4562-b3fc-2c963f66afa6'
    ),
):
    """# Show a tweet

    This path operation shows a tweet in the app

    Parameters:
    - tweet_id: str

    Returns:
    - Json with a tweet in the app, with the following keys:
        - tweet_id: UUID
        - content: str
        - created_at: datetime
        - updated_at: Optional[datetime]
        - by: User
    """
    with open('tweets.json', 'r', encoding='utf-8') as f:
        results = json.loads(f.read())
        id = str(tweet_id)
        for data in results:
            if data["tweet_id"] == id:
                return data
            else:
                raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"¡This tweet_id doesn't exists!"
            )

### Delete a tweet
@app.delete(
    path="/tweets/{tweet_id}/delete",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Delete a Tweet",
    tags=["Tweets"]
)
def delete_a_tweet(
    tweet_id: str = Path(
        ...,
        title='Tweet ID',
        description='This is the ID of the tweet to be deleted',
        example='3fa85f64-5717-4562-b3fc-2c963f55afb7'
    ),
):
    """# Delete a tweet

    This path operation deletes a tweet in the app

    Parameters:
    - tweet_id: str

    Returns:
    - Json with deleted tweet data:
        - tweet_id: UUID
        - content: str
        - created_at: datetime
        - updated_at: Optional[datetime]
        - by: User
    """
    with open('tweets.json', 'r+', encoding='utf-8') as f:
        deletion = json.loads(f.read())
        id = str(tweet_id)
        for data in deletion:
            if data['tweet_id'] == id:
                deletion.remove(data)
                with open("tweets.json", "w", encoding="utf-8") as f:
                    f.seek(0)
                    f.write(json.dumps(deletion))
                return data
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="¡This tweet_id doesn't exist!"
            )
### Update a tweet
@app.put(
    path="/tweets/{tweet_id}/update",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Update a Tweet",
    tags=["Tweets"]
)
def update_a_tweet(
    tweet_id: UUID = Path(
            ...,
            title="Tweet ID",
            description="This is the tweet ID",
            example="3fa85f64-5717-4562-b3fc-2c963f66afa6"
        ),
        content: str = Form(
        ...,
        min_length=1,
        max_length=256,
        title="Tweet content",
        description="This is the content of the tweet",
        )
    ):
    """
    # Update Tweet content

    This path operation updates the information of a tweet in the app and saves it in the database

    Parameters:
    - tweet_id: UUID
    - contet:str

    Returns a json with:
    - tweet_id: UUID
    - content: str
    - created_at: datetime
    - updated_at: datetime
    - by: user: User
    """
    tweet_id = str(tweet_id)
    with open("tweets.json", "r+", encoding="utf-8") as f:
        results = json.loads(f.read())
    for tweet in results:
        if tweet["tweet_id"] == tweet_id:
            tweet['content'] = content
            tweet['updated_at'] = str(datetime.now())
            print(tweet)
            with open("tweets.json", "w", encoding="utf-8") as f:
                f.seek(0)
                f.write(json.dumps(results))
            return tweet
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="¡This tweet_id doesn't exist!"
        )