from flask_pymongo import PyMongo

class User(PyMongo):
    
    def save_user_to_db(self, data):
        self.db.users.insert_one(data)
        return {"message": "User created successfully."}

    def find_user_by_username(self, username):
        result = self.db.users.find_one({'username' : username})
        return result
    
    

