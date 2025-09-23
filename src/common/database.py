blocked_token_db = set()
user_db = []
session_db = {}

class UserId():
    id = 0
    
    @classmethod
    def get_next(self):
        # id 1 증가 후 반환
        self.id += 1
        return self.id