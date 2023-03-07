import requests
import json
import random
 
    
    
def movie_show_generator():
    
    users_input = requests.form.get("next")
    url1 = "https://online-movie-database.p.rapidapi.com/title/v2/get-popular-movies-by-genre"
    querystring1 = {"genre": users_input, "limit": "100"}
    headers = {
        "X-RapidAPI-Key": "4aa56d7288msh5be0286e95c8c10p160380jsnfce8a0c61ccd",
        "X-RapidAPI-Host": "online-movie-database.p.rapidapi.com"
    }
    response1 = requests.request(
        "GET", url1, headers=headers, params=querystring1)
    ids = []
    data1 = json.loads(response1.text)

    for id in data1:
        ids.append(id.split("/")[2])
        # res = [sub[2:] for sub in ids]
    choice = random.choice(ids)

    # uses the choice which is an IMDB titleid to asign run through this API to determine the title name, 1000 daily limit
    url2 = "http://www.omdbapi.com/?apikey=b2e0b78b&"
    querystring2 = {"i": choice}
    response2 = requests.request("GET", url2, params=querystring2)
    data2 = json.loads(response2.text)
    Movie_Title_Name = data2['Title']
    print(Movie_Title_Name)

    # gets the image for the title ID from the url2 API only 500 requests/month
    url3 = "https://online-movie-database.p.rapidapi.com/title/get-images"
    querystring3 = {"tconst": choice, "limit": "1"}
    headers = {
        "X-RapidAPI-Key": "4aa56d7288msh5be0286e95c8c10p160380jsnfce8a0c61ccd",
        "X-RapidAPI-Host": "online-movie-database.p.rapidapi.com"
    }
    response3 = requests.request(
        "GET", url3, headers=headers, params=querystring3)
    data3 = json.loads(response3.text)
    movie_image_url = data3["images"][0]["relatedTitles"][0]["image"]["url"]
    print(movie_image_url)