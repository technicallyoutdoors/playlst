import random
import string

def generate_code():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return code

code = generate_code()