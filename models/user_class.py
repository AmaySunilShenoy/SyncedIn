from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, email, password,profile_picture):
         self.id = id
         self.username = username
         self.email = email
         self.password = password
         self.profile_picture = profile_picture
         self.authenticated = False   
         
         
    def is_active(self):
         return self.is_active()    
    
    def is_anonymous(self):
         return False    
    
    def is_authenticated(self):
         return self.authenticated    
    
    def is_active(self):
         return True    
    
    def get_id(self):
         return self.id