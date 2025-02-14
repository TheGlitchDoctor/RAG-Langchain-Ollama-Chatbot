import requests
 
url = "http://10.18.28.210:5555/chatbot"
#url = "http://localhost:5555/chatbot"

payload = {
    "question": "What is py fluent?",
    "chat_history": "",
    "collection_name": "pyfluent"
}
headers = {
    "Content-Type": "application/json"
}
 
response = requests.post(url, headers=headers, json=payload)
 
print(response.text)