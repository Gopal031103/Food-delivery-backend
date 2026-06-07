# from fastapi import FastAPI
# from schemas import User

# app = FastAPI()

# users = []

# @app.get("/")
# def home():
#     return {"message": "Food Delivery API Running"}

# @app.post("/register")
# def register(user: User):
#     users.append(user)
#     return {
#         "message": "User Registered Successfully",
#         "user": user
#     }

# @app.get("/users")
# def get_users():
#     return users

# @app.get("/users/{id}")
# def get_user(id: int):
#     if id >= len(users):
#         return {"error": "User not found"}

#     return users[id]


