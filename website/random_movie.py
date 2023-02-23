import requests
import json
import random
from tmdbv3api import TMDb
from tmdb_api_key import api_key
from tmdbv3api import Movie


users_input = input("What genre of movie do you want to find? ")

url1 = "https://online-movie-database.p.rapidapi.com/title/v2/get-popular-movies-by-genre"

querystring1 = {"genre": users_input, "limit": "100"}

headers = {
    "X-RapidAPI-Key": "20719788e5msh46d7f8c7ed9abd9p1d8da2jsnb3f8e9ee7b85",
    "X-RapidAPI-Host": "online-movie-database.p.rapidapi.com"
}


response1 = requests.request("GET", url1, headers=headers, params=querystring1)


ids = []

data1 = json.loads(response1.text)


for id in data1:
    ids.append(id.split("/")[2])
    # res = [sub[2:] for sub in ids]

choice = random.choice(ids)


url2 = "http://www.omdbapi.com/?apikey=b2e0b78b&"


querystring2 = {"i": choice}

response2 = requests.request("GET", url2, params=querystring2)

data2 = json.loads(response2.text)

Title_Name = data2['Title']

print(Title_Name)

url3 = "https://online-movie-database.p.rapidapi.com/title/get-images"

querystring3 = {"tconst": choice, "limit": "1"}

headers = {
    "X-RapidAPI-Key": "20719788e5msh46d7f8c7ed9abd9p1d8da2jsnb3f8e9ee7b85",
    "X-RapidAPI-Host": "online-movie-database.p.rapidapi.com"
}

response3 = requests.request("GET", url3, headers=headers, params=querystring3)


data3 = json.loads(response3.text)

image_url = data3["images"][0]["relatedTitles"][0]["image"]["url"]


print(image_url)



# image_url = data3['image']


# url = "https://online-movie-database.p.rapidapi.com/title/v2/find"

# querystring = {"title": "adventure", "limit": "20",
#                "sortArg": "moviemeter,asc", "genre": }

# headers = {
#     "X-RapidAPI-Key": "20719788e5msh46d7f8c7ed9abd9p1d8da2jsnb3f8e9ee7b85",
#     "X-RapidAPI-Host": "online-movie-database.p.rapidapi.com"
# }

# response = requests.request("GET", url, headers=headers, params=querystring)

# # print(response.text)

# data = json.loads(response.text)

# print(data)
