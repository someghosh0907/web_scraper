from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
scraped_data = []
def my_view(request):
    context = {'author': 'hello world'}
    return render(request, 'index.html', context)

def get_data(request,make=None, model=None,scraper_name=None):
    # make = request.GET.get('make',None)
    make="Ford"
    model="Mustang"
    # model = request.GET.get('model',None)
# Step 1: Choose the URL you want to scrape
    # if make is not None or model is not None:
    if scraper_name is not None:
        scraper_name=str(scraper_name)
    if scraper_name is None:
        scraper_name = "scrape new"
    url1 = f"https://carswitch.com/uae/used-cars/search?keyword={make}%20{model}"
    url2 = "https://syarah.com/filters?text={make}%20{model}"
    url3 = "https://ly.opensooq.com/en/cars?term=ford"
    url4 = f"https://www.gogomotor.com/en/used-cars/surveyed-searchkey-{make}%20{model}"

# Step 2: Fetch the page content
    response1 = requests.get(url1)
    response2 = requests.get(url2)
    response3 = requests.get(url3)
    response4 = requests.get(url4)
    if response1.status_code == 200:
     # Step 3: Parse HTML with BeautifulSoup
        soup1 = BeautifulSoup(response1.content, "html.parser")
        soup2 = BeautifulSoup(response2.content, "html.parser")
        soup3 = BeautifulSoup(response3.content, "html.parser")
        soup4 = BeautifulSoup(response4.content, "html.parser")
     # Soup 1-----------------------------------------------------------------------------------------------------
        global scraped_data
        for card in soup1.find(id='main-listing-div').find_all("div", {"class": "card-body"}):
        # arr1=[]
            obj={}
            name = card.find("h2")
            year = card.find("span",{"class":"item year"})
            mileage=card.find("span",{"class":"item mileage"})
            price=card.find("span",{"class":"full-price"})
            img=card.find("a",{"class":"img-wrapper"})
            # img=img.find("img","src")
            # print("imggggggggggggg",img)
            obj["img"]=img
            obj["year"]=year.text
            obj["price"]=price.text
            obj["name"]=name.text
            obj["mileage"]=mileage.text
            # obj[scraper_name]=obj
            scraped_data.append(obj)
        # return render(request, 'scrape.html', {'data': arr})
        print("Soup 1 data:", scraped_data)
        return render(request, 'scraped_data.html', {'arr': scraped_data})
        # return ("okokokokokokokokok")

    else:
        print("Failed to retrieve the web page")
        return("Bad luck")