import requests  

url = 'http://localhost:8000/api/v1/accounts/login-users/'  # your token endpoint  
data = {  
    'email': 'test@test.com',  
    'password': 'test'  
}  

response = requests.post(url, json=data)  
tokens = response.json()  

access_token = tokens.get('access')  
print('JWT Token:', access_token) 


"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ3MTM2MjM4LCJpYXQiOjE3NDU5MjY2MzgsImp0aSI"