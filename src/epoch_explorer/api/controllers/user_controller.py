from epoch_explorer.models.user import User
from epoch_explorer.core.logger import log

def handle_user_request(username: str):
    user = User(username)
    log(f"Handling user: {username}")
    return user.greet()
