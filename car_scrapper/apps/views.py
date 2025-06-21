from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import get_data


cars = {
    "Toyota": ["Camry", "Supra", "Fortuner"],
    "Honda": ["Accord", "Civic"],
    "Ford": ["Mustang", "Taurus", "F-150"],
    "Chevrolet": ["Camaro", "Corvette", "TrailBlazer"]
}

scrape_arr=[]
scraped_data=[{'img': None, 'year': ' 2015 ', 'price': '\nAED 39,000AED 43,500', 'name': 'Ford Mustang  V6 3.7L', 'mileage': ' 96,500 KM '}, {'img': None, 'year': ' 2019 ', 'price': '\nAED 121,000AED 133,500', 'name': 'Ford Mustang GT V8 5.0L', 'mileage': ' 53,500 KM '}, {'img': None, 'year': ' 2018 ', 'price': '\nAED 120,000', 'name': 'Ford Mustang GT premium  V8 5.0L', 'mileage': ' 88,500 KM '}, {'img': None, 'year': ' 2019 ', 'price': '\nAED 40,000', 'name': 'Ford Mustang V4 2.3L', 'mileage': ' 155,000 KM '}, {'img': None, 'year': ' 2017 ', 'price': '\nAED 69,750', 'name': 'Ford Mustang Mustang', 'mileage': ' 87,000 KM '}, {'img': None, 'year': ' 2015 ', 'price': '\nAED 39,000AED 43,500', 'name': 'Ford Mustang  V6 3.7L', 'mileage': ' 96,500 KM '}, {'img': None, 'year': ' 2019 ', 'price': '\nAED 121,000AED 133,500', 'name': 'Ford Mustang GT V8 5.0L', 'mileage': ' 53,500 KM '}, {'img': None, 'year': ' 2018 ', 'price': '\nAED 120,000', 'name': 'Ford Mustang GT premium  V8 5.0L', 'mileage': ' 88,500 KM '}, {'img': None, 'year': ' 2019 ', 'price': '\nAED 40,000', 'name': 'Ford Mustang V4 2.3L', 'mileage': ' 155,000 KM '}, {'img': None, 'year': ' 2017 ', 'price': '\nAED 69,750', 'name': 'Ford Mustang Mustang', 'mileage': ' 87,000 KM '}]
def my_view(request):
    context = {'author': 'Gaurav Singhal'}
    print("Rendering index.html with context:", context)  # Debugging output
    return render(request, 'index.html', context)

def fun(request,make=None, model=None,scraper_name=None):
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
        print("Soup 1 data:", scrape_arr)
        return render(request, 'scraped_data.html', {'arr': scraped_data})
        # return ("okokokokokokokokok")

    else:
        print("Failed to retrieve the web page")
        return("Bad luck")
    
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Here you would typically check the credentials against your database
        if len(username)!=0 and len(password)!=0:  # Example check
            return render(request, 'dashboard.html', {'message': 'Login successful!'})
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def dashboard(request):
    # This view would typically fetch user-specific data
    print("In Dashboard View")
    return render(request, 'dashboard.html', {"scrape_arr":scrape_arr})

def create_scrape(request):
    scrape_arr
    # This view handles the form submission for creating a scrape job
    if request.method == 'POST':
        # Extract form data
        scraper_name = request.POST.get('scraper_name')
        website = request.POST.get('website')
        make = request.POST.get('make')
        model = request.POST.get('model')
        min_year = request.POST.get('min_year')
        max_year = request.POST.get('max_year')
        city = request.POST.get('city')
        # fuel_type = request.POST.get('fuel_type')
        # transmission = request.POST.get('transmission')
        # frequency = request.POST.get('frequency')

        # Here you can save the data to your database or process it as needed
        # For example, if you have a model named ScrapeJob:
        # from .models import ScrapeJob
        # ScrapeJob.objects.create(
        #     scraper_name=scraper_name,
        #     website=website,
        #     make=make,
        #     model=model,
        #     min_year=min_year,
        #     max_year=max_year,
        #     city=city,
        #     fuel_type=fuel_type,
        #     transmission=transmission,
        #     frequency=frequency,
        # )
        scrape_obj={
            'scraper_name': scraper_name,
            'website': website,
            'make': make,
            'model': model,
            'min_year': min_year,
            'max_year': max_year,
            'city': city,
            'status': 'Active',  # Assuming you want to track the status of the scrape job
            # 'fuel_type': fuel_type
            }

        scrape_arr.append(scrape_obj)
        print("Scrape job created:", scrape_obj)
        print("Current scrape_arr:", scrape_arr)

        # Optionally, add a success message
        # messages.success(request, 'Scrape job created successfully!')
        # Redirect to a success page or back to the form
        return redirect('dashboard')  # Redirect to the dashboard after creating a scrape job

    # If GET (or any other method), render the form
    return render(request, 'create_scrape.html')

def get_scraped_data(request,make=None, model=None,scraper_name=None):
    # This view would typically fetch the scraped data based on make and model
    # print("Scraped data:", scrape_arr[scrape_id])
    scraped_data=get_data(request,make,model)
    print("hrere",scraped_data)
    return render(request, 'scraped_data.html', {'scraped_data':  scraped_data})
