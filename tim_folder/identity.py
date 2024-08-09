import re
import uuid

class Identity:
    static_length = 32

    @staticmethod
    def create_id() -> str:
        u_id = str(uuid.uuid4())
        return re.sub(r'[^A-Za-z0-9]', '', u_id)