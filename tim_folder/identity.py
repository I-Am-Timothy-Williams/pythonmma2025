import re
import uuid

class Identity:
    # Static class variable to define the length of the ID
    static_length = 32

    @staticmethod
    def create_id() -> str:
        # Generate a UUID (universally unique identifier)
        u_id = str(uuid.uuid4())
        # Use a regular expression to remove any non-alphanumeric characters
        return re.sub(r'[^A-Za-z0-9]', '', u_id)
