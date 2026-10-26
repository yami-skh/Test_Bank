# import requests
# import pytest
import random

def generate_user():
    return "user"+ str(random.randint(0,9999999))

print(generate_user())
