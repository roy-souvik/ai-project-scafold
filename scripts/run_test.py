from epoch_explorer.api.controllers.user_controller import handle_user_request
from epoch_explorer.core.config import show_config

if __name__ == "__main__":
    # Display loaded configuration
    show_config()

    result = handle_user_request("Sourav")
    print(result)