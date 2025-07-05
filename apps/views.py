from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect
from django.db.models.query import QuerySet
from .utils import get_data_from_carswitch_uae,get_data_from_opensooq_ksa,get_data_from_carswitch_ksa,get_data_from_opensooq_uae
from .models import CarQuery,CarListing
from django.db.models import Q

# cars = {
#     "Toyota": ["Camry", "Supra", "Fortuner"],
#     "Honda": ["Accord", "Civic"],
#     "Ford": ["Mustang", "Taurus", "F-150"],
#     "Chevrolet": ["Camaro", "Corvette", "TrailBlazer"]
# }

websitename=None
print("websitename---------------------------------------------------",websitename)

def icontains(val, target):
        return not val or (target and val.lower() in target.lower())
scrape_arr=[]
scraped_data=[]

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
    get_car_query_list=CarQuery.objects.all()
    print("------------------------------------------------",get_car_query_list)
    print("In Dashboard View")
    return render(request, 'dashboard.html', {"scrape_arr":get_car_query_list})

def create_scrape(request):
    # scrape_arr
    # This view handles the form submission for creating a scrape job
    if request.method == 'POST':
        # Extract form data
        scraper_name = request.POST.get('scraper_name')
        website = request.POST.get('website')
        make = request.POST.get('make')
        model = request.POST.get('model')
        min_year = request.POST.get('min_year')
        max_year = request.POST.get('max_year')
        city = request.POST.get('city',"null")
        country=request.POST.get('country')
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
        # websitename=website
        create_car_scrape_obj=CarQuery.objects.create(
            scraper_name=scraper_name,
            car_make=make,
            car_model=model,
            country=country,
            website=website,
            city=city,
            status="Active"
        )
        create_car_scrape_obj.save()
        scrape_obj={
            'scraper_name': scraper_name,
            'website': website,
            'make': make,
            'model': model,
            'min_year': min_year,
            'max_year': max_year,
            'city': city,
            'country':country,
            'status': 'Active',  # Assuming you want to track the status of the scrape job
            # 'fuel_type': fuel_type
            }

        scrape_arr.append(scrape_obj)
        print("Scrape job created:", scrape_obj)
        print("Current scrape_arr:", scrape_arr)

        websitename=scrape_arr[0]['website']

        print("websitename",websitename)

        # Optionally, add a success message
        # messages.success(request, 'Scrape job created successfully!')
        # Redirect to a success page or back to the form
        return redirect('dashboard')  # Redirect to the dashboard after creating a scrape job

    # If GET (or any other method), render the form
    return render(request, 'create_scrape.html')

def get_scraped_data(request):
    # This view would typically fetch the scraped data based on make and model
    # print("Scraped data:", scrape_arr[scrape_id])
    # website=None
    # print("make",make,"model",model,"uuid",uuid)
    # print("incall",website,country)
    print("req data--------------",request.GET)
    print("re.post--------------------",request.POST)
    uuid= request.GET.get('uuid', '')
    make= request.GET.get('make', '')
    model= request.GET.get('model', '')
    website= request.GET.get('website', '')
    # uuid= request.POST.get('uuid', '')
    # uuid=uuid.replace('-', '')
    country= request.GET.get('country', '')
    city= request.GET.get('city', '')
    # Instance of CarListing
    scraped_data = CarListing.objects.filter(query_id=uuid,make=make,model=model)
    print("INSTANCE",scraped_data)
    # title_filter= request.POST.get('title-filter', '').strip()
    if request.method=='POST':
        mileage_hidden_low= request.POST.get('mileage-hidden-low', '')
        print("mileage_hidden_low",mileage_hidden_low)
        mileage_hidden_high=request.POST.get("mileage-hidden-high",'')
        print("mileage_hidden_high",mileage_hidden_high)
        price_hidden_low=request.POST.get("price-hidden-low",'')
        print("price_hidden_low",price_hidden_low)
        price_hidden_high=request.POST.get("price-hidden-high",'')
        print("price_hidden_high",price_hidden_high)
        if price_hidden_low==0 and price_hidden_high==200000:
            price_hidden_low=None
            price_hidden_high=None
        if mileage_hidden_low==0 and mileage_hidden_high==200000:
            mileage_hidden_low=None
            mileage_hidden_high=None
        print("PRICE HIDDEN LOW",price_hidden_low)  
        print("PRICE HIDDEN HIGH",price_hidden_high)
        make_filter= request.POST.get('make-filter', '').strip()
        model_filter= request.POST.get('model-filter', '').strip()
        year_filter= request.POST.get('model-year-filter', '').strip()
        print("YEAR-------------------------------------------------------------------------",year_filter)
        # mileage_filter= request.POST.get('mileage-filter', '')
        # mileage_filter_low=request.POST.get('mileage-filter-low','')
        # mileage_filter_high=request.POST.get('mileage-filter-high','')
        # price_filter_low=request.POST.get('price-filter-low','')
        # price_filter_high=request.POST.get('price-filter-high','')
        # total_mileage=mileage_filter_high-mileage_filter_low
        city_filter= request.POST.get('city-filter', '').strip()
        fuel_type_filter= request.POST.get('fuel-type', '').strip()
        transmission_filter= request.POST.get('transmission', '').strip()
        vehicle_listing_date_filter= request.POST.get('vehicle-listing-date-filter', '').strip()
        vehicle_exit_date_filter= request.POST.get('vehicle-exit-date-filter', '').strip()
        color_filter= request.POST.get('color-filter', '').strip()
        # year_filter = request.GET.get('date-filter', '').strip()
        trim_filter = request.POST.get('trim-filter', '').strip()
        # print("trim_filter",trim_filter if trim_filter else None)
        # price_filter = request.POST.get('price-filter', '')
        # if price_hidden_low:
        #     scraped_data = scraped_data.filter(price__gte=price_hidden_low)
        #     print("PRICE HIDDEN LOW",scraped_data)
        # if price_hidden_high:
        #     scraped_data = scraped_data.filter(price__lte=price_hidden_high)
        #     print("PRICE HIDDEN HIGH",scraped_data)
        # if mileage_hidden_low:
        #     scraped_data = scraped_data.filter(mileage__gte=mileage_hidden_low)
        #     print("MILEAGE HIDDEN LOW",scraped_data)
        # if mileage_hidden_high:
        #     scraped_data = scraped_data.filter(mileage__lte=mileage_hidden_high)
        #     print("scraped_data before filter",scraped_data)
        scraped_data=scraped_data.filter(
        Q(make__icontains=make_filter) &
        Q(model__icontains=model_filter) &
        Q(year__icontains=year_filter) &
        # Q(mileage__icontains=total_mileage) &
        Q(city__icontains=city_filter) & 
        Q(fuel_type__icontains=fuel_type_filter) & 
        Q(transmission__icontains=transmission_filter) & 
        Q(color__icontains=color_filter) & 
        Q(vehicle_listing_date__icontains=vehicle_listing_date_filter) & 
        Q(vehicle_exit_date__icontains=vehicle_exit_date_filter) & 
        Q(trim__icontains=trim_filter) &
        Q(price__gte=price_hidden_low) if price_hidden_low is not None else Q() &
        Q(price__lte=price_hidden_high) if price_hidden_high is not None else Q() &
        Q(mileage__gte=mileage_hidden_low) if mileage_hidden_low is not None else Q() &
        Q(mileage__lte=mileage_hidden_high) if mileage_hidden_high is not None else Q()
        )

        # if price_hidden_low:
        #     filter_price_data = scraped_data.filter(price__gte=price_hidden_low)
        #     print("PRICE HIDDEN LOW",scraped_data)
        # if price_hidden_high:
        #     filter_price_data = scraped_data.filter(price__lte=price_hidden_high)
        #     print("PRICE HIDDEN HIGH",scraped_data)
        # if mileage_hidden_low:
        #     scraped_data = scraped_data.filter(mileage__gte=mileage_hidden_low)
        #     print("MILEAGE HIDDEN LOW",scraped_data)
        # if mileage_hidden_high:
        #     scraped_data = scraped_data.filter(mileage__lte=mileage_hidden_high)
        #     print("MILEAGE HIDDEN HIGH",scraped_data)
        # Q(price__icontains=price_filter))
        print("FILTERED DATA------------------------------------------------",scraped_data)
    # if country is not None and city is not None:
    #     scraped_data = CarListing.objects.filter(query_id=uuid,make=make,model=model,website=website)
    # if city is None or city == "none":#RUNS THIS WHEN CITY IS NOT PRESENT
    print("scraped",scraped_data)
    if (not scraped_data
        or (isinstance(scraped_data, QuerySet) and scraped_data.count() == 0)):
        if website=="All" and country=="UAE":
            scraped_data_=get_data_from_carswitch_uae(request,make,model,uuid,country,city)
            print("UAE SCRAPED DATA",scraped_data_)
            scraped_data__=get_data_from_opensooq_uae(request,make,model,uuid,country,city)
            scraped_data=list(scraped_data_)+list(scraped_data__)    
        elif website=="All" and country=="KSA":
            scraped_data_=get_data_from_carswitch_ksa(request,make,model,uuid,country,city)
            print("UAE SCRAPED DATA",scraped_data_)
            scraped_data__=get_data_from_opensooq_ksa(request,make,model,uuid,country,city)
            scraped_data=list(scraped_data_)+list(scraped_data__)
        elif website=="All" and country=="All":
            print("In all web all country")
            get_data_from_carswitch_uae(request,make,model,uuid,country,city)
            print("1")
            get_data_from_opensooq_uae(request,make,model,uuid,country,city)
            print("2")
            get_data_from_carswitch_ksa(request,make,model,uuid,country,city)
            print("3")
            get_data_from_opensooq_ksa(request,make,model,uuid,country,city)
            print("4")
        elif website=="carswitch":
            if country=="UAE":
                scraped_data=get_data_from_carswitch_uae(request,make,model,uuid,country,city)
            elif country=="KSA":
                scraped_data=get_data_from_carswitch_ksa(request,make,model,uuid,country,city)
            elif country=="All":
                scraped_data_=get_data_from_carswitch_uae(request,make,model,uuid,country,city)
                scraped_data__=get_data_from_carswitch_ksa(request,make,model,uuid,country,city)
                # scraped_data=list(scraped_data_)+list(scraped_data__)
                # print("JOINED DATA CARSWITCH",scraped_data)
        elif website=="opensooq":
            if country=="KSA":
                scraped_data=get_data_from_opensooq_ksa(request,make,model,uuid,country,city)
            elif country=="UAE":
                scraped_data=get_data_from_opensooq_uae(request,make,model,uuid,country,city)
            elif country=="All":
                get_data_from_opensooq_ksa(request,make,model,uuid,country,city)
                get_data_from_opensooq_uae(request,make,model,uuid,country,city)
                # scraped_data=list(scraped_data_)+list(scraped_data__)
                # print("JOINED DATA OPENSOOQ",scraped_data)
        print("hrere",scraped_data)
    return render(request, 'scraped_data.html', {
        'scraped_data': scraped_data, 
        # in locals() else None,
        'make':make,
        'model':model,
        'website': website,
        'uuid': uuid,
        'country':country,
        'city':city
    })

def item_price_list(request,scraped_data):
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    items = CarListing.objects.all()
    if min_price:
        items = items.filter(price__gte=min_price)
    if max_price:
        items = items.filter(price__lte=max_price)
    return render(request, 'item_list.html', {
        'items': items,
        'min_price': min_price or '',
        'max_price': max_price or '',
    })
def get_ksa(request):
    make="Toyota"
    model="Corolla"
    get_cars=get_data_from_carswitch_ksa(request,make,model)
    return get_cars