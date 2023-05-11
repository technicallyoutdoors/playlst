import random 
import requests
import json



random_page = random.randint(0, 100)

url1 = "https://api.themoviedb.org/3/discover/movie?api_key=28dd9fa4c4a210cd3dc589981c8fb66a&language=en-US&region=US&sort_by=popularity.desc&include_adult=false&include_video=false&page=" + \
    str(random_page) + "&with_watch_providers=netflix%2C%20hulu%2C%20amazon&with_watch_monetization_types=flatrate"
    
request1 = requests.get(url1)

data1 = request1.json()

titles = data1.get('results')
random_title = random.choice(titles)
random_id = random_title.get('id')

url2 = "https://api.themoviedb.org/3/movie/" + str(random_id) + "?api_key=28dd9fa4c4a210cd3dc589981c8fb66a&language=en-US"

request2 = requests.get(url2)

data2 = request2.json()

print(data2)

print(random_id)

random_title_image = random_title.get('poster_path')
url_append = "https://image.tmdb.org/t/p/original"
full_path_random_title_image = url_append + random_title_image
print(full_path_random_title_image)
over_view = random_title.get('overview')

title = random_title.get('title')

print(title)

print(over_view)

    
    
# url2 = "https://api.themoviedb.org/3/watch/providers/movie?api_key=28dd9fa4c4a210cd3dc589981c8fb66a&language=en-US&watch_region=US"

# request2 = requests.get(url2)

# data2 = request2.json()

# print(data2)
    
    
    