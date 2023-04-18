import requests
import json

url4 = "https://online-movie-database.p.rapidapi.com/title/get-overview-details"
querystring4 = {"tconst":choice,"currentCountry":"US"}
headers4 = {
	"X-RapidAPI-Key": "ed1e6a5735mshdcb3f871a40c3abp18177ajsn0bb3cfaa8b87",
	"X-RapidAPI-Host": "online-movie-database.p.rapidapi.com"
}
response4 = requests.request("GET", url4, headers=headers4, params=querystring4)

data5 = json.loads(response4.text)
short_description = data5['plotSummary']['text']


print(short_description)