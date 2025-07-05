from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import webbrowser
import re
from .models import CarListing,CarQuery
from datetime import datetime, timedelta
import re

def extract_max_number_from_mileage(text):
    # Find all groups of digits (with optional commas)
    numbers = re.findall(r'\d[\d,]*', text)
    # Convert to integers after removing commas
    numbers = [int(num.replace(',', '')) for num in numbers]
    # Return the maximum, or None if no numbers found
    return max(numbers) if numbers else None
def extract_currency_and_amount(text):
    # This regex matches a 3-letter currency code and a number (with optional comma)
    arr=[]
    match = re.search(r'([A-Za-z]{3})\s*([\d,]+)', text)
    if match:
        currency = match.group(1)
        amount = int(match.group(2).replace(',', ''))
        
        return amount
    return None

def extract_amount_opensooq(text):
    amount_str = text.split()[0]
    amount_str = amount_str.replace(",", "")  # [1][2][3][4][5][6]
    return int(amount_str)
scraped_data = []
def week_to_date(week):
    # week=int(week)
    """
    Converts 'week' (number of weeks ago) to a date string in dd/mm/yyyy format.
    Example: week=2 returns the date 2 weeks ago from today.
    """
    target_date = datetime.today() - timedelta(weeks=week)
    return target_date.strftime('%d/%m/%Y')
def my_view(request):
    context = {'author': 'hello world'}
    return render(request, 'index.html', context)

def get_trim(full_string, prefix):
    if full_string.startswith(prefix):
        return full_string[len(prefix):].strip()
    else:
        return full_string

#Checks if any field in carlisting has a null value or not
def all_fields_filled(car_listing_obj):
    """
    Returns False if any attribute of car_listing_instance is None or blank (for CharFields).
    Returns True only if all fields have non-None, non-blank values.
    """
    # List all field names you want to check (excluding auto fields and nullable fields if desired)
    fields_to_check = [
        # 'query', 'image_url', 'make', 'model', 'price', 'mileage', 'city', 'year',
        'transmission', 'fuel_type', 'color', 'vehicle_listing_date', 'seller_type', 
    ]
    for field in fields_to_check:
        value = getattr(car_listing_obj, field, None)
        # For CharFields, also check for empty string
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return False
    return True
def get_data_from_opensooq_ksa(request, make=None, model=None,uuid=None,country=None,city=None):
    car_query_instance = CarQuery.objects.get(uuid=uuid)
    # url = f"https://sa.opensooq.com/en/cars?search=true&term={make}+{model}"
    if city=="" or city=="All":
        url = f"https://sa.opensooq.com/en/cars?search=true&term={make}+{model}"
    elif city is not None:
        city=int(city)
        city=get_city(city)
        url = f"https://sa.opensooq.com/en/{city}/cars/all?search=true&term={make}+{model}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Get the listing section
    main_div = soup.find("div", id='serpMainContent')

    # Get anchors and corresponding image divs
    anchors = main_div.find_all('a', href=True)
    img_divs = main_div.find_all("div", class_="postImgCont relative radius-8 overflowHidden me-16 grayBg")

    scraped_data = []

    # Loop through anchors and their corresponding image divs (zip safely)
    for a, img_div in zip(anchors, img_divs):
        href = a['href']
        full_url = f"https://sa.opensooq.com{href}"
        print("Visiting:", full_url)

        # Try to extract image URL
        img_tag = img_div.find("img")
        img_url = img_tag.get("data-src") or img_tag.get("src") if img_tag else None

        
        detail_response = requests.get(full_url)
        detail_soup = BeautifulSoup(detail_response.content, "html.parser")
        get_price=detail_soup.find("div",class_="flex alignItems relative priceColor bold font-30 width-fit").text
        get_amt=extract_amount_opensooq(get_price)   #priceeee
        specs_section = detail_soup.find("ul", class_="flex flexSpaceBetween flexWrap mt-8")
        if not specs_section:
            print("No specs section found, skipping...")
            continue

        obj = {}
        all_items = specs_section.find_all("li")

        for item in all_items:
            key = item.find("p", class_="noWrap")
            value = item.find("a") or item.find("span")
            if key and value:
                key_text = key.get_text(strip=True)
                value_text = value.get_text(strip=True)
                # print("key_text:", key_text, "| value_text:", value_text)

                key_map = {
                    "Year": "Year",
                    "Fuel": "Fuel",
                    "Trim": "Trim",
                    "Kilometers": "Kilometers",
                    "Transmission": "Transmission",
                    "Exterior Color": "Exterior_Color",
                    "City": "City",
                    "Car Make": "Car_Make",
                    "Model": "Model",
                }

                if key_text in key_map:
                    obj[key_map[key_text]] = value_text
                

        if obj:
            obj["Listing_URL"] = full_url
            obj["Image_URL"] = img_url
            obj["Currency"] = "SAR"  # Default to SAR if not found
            obj["Price"]=get_amt
            obj['available_date']='22.03.2025'
            obj['release_date']='-'
            obj['listing_period']='-'
            obj['seller_type']='Individual'
            print("Extracted:", obj)
            mileage=extract_max_number_from_mileage(obj.get("Kilometers",""))
        create_car_listing=CarListing.objects.create(
            query=car_query_instance,
            image_url=obj["Image_URL"] ,
            make=obj.get('Car_Make', ""),
            model= obj.get("Model", ""),
            trim=obj.get("Trim",""),
            price=obj.get("Price",""),
            mileage=mileage,
            city=obj.get("City",""),
            year=obj.get("Year",""),
            currency=obj.get("Currency", ""),  # Added currency field
            transmission=obj.get("Transmission",""),
            fuel_type=obj.get("Fuel",""),
            color=obj.get("Exterior_Color",""),
            vehicle_listing_date=obj.get('available_date',""),
            vehicle_exit_date=obj.get('release_date',""),
            seller_type="Individual",
            website="opensooq",
            website_url=full_url
        )
        create_car_listing.save()
        # print("Created-------------------------------------------------",obj["Model"])
        scraped_data.append(obj)

    get_vehicles=get_car_info(make,model,uuid)
    return get_vehicles
# for d in data_list:
#     print(d)
# -------------------------------------Carswitch----------------------------------------


def get_data_from_carswitch_uae(request,make,model,uuid,country,city):
    print("In UAE--------------------------------------------------------------------")
    # make="Porsche"
    # model="Panamera"
    car_query_instance = CarQuery.objects.get(uuid=uuid)
    print("car_query_instance",car_query_instance,uuid)
    # https://carswitch.com/uae/used-cars/search?cities=1&keyword=Toyota%20Corolla    #WHEN SEARCHING BY CITY NAME
    if city=="" or city=="All":
        url1 = f"https://carswitch.com/uae/used-cars/search?keyword={make}%20{model}"     #WHEN WORKING WITH UAE    
    elif city is not None:
        city=int(city)
        url1=f"https://carswitch.com/uae/used-cars/search?cities={city}&keyword={make}%20{model}"
    # Step 2: Fetch the page content
    response1 = requests.get(url1)
    prefix=make+" "+model
    soup1 = BeautifulSoup(response1.content, "html.parser")
    car_cards = soup1.find_all("div", class_="card-body")
    image_holders=soup1.find_all(class_=["image-holder"])

    scraped_data = []

    for card, img_holder in zip(car_cards, image_holders):
        # Extract car title or summary
        obj={}
        year = card.find("span",{"class":"item year"})
        mileage=card.find("span",{"class":"item mileage"})
        price=card.find("span",{"class":"full-price"})
        amt= extract_currency_and_amount(price.text)
        obj['Model'] = model
        obj['Car_Make'] = make
        obj["Year"] = year.text
        # obj['title'] = card.get_text(strip=True)
        obj["title"] = card.find("h2").text
        obj["Currency"] = "AED"
        obj["Price"] = amt
        # obj["name"]=name.text
        obj["Kilometers"]=mileage.text
        obj['release_date']='-'
        obj['listing_period']='-'
        obj['seller_type']='Individual'
        # obj[scraper_name]=obj
        # print("title",title)
        # Extract image src
        img_tag = img_holder.find("img")
        # print("img_tag",img_tag)
        img_src = None
        if img_tag:
            img_src = img_tag.get("src") or "https:"+img_tag.get("data-src")
            obj['Image_URL']=img_src
        #to redirect to href target page
        anchor = img_holder.find('a')
        new_link=None
        if anchor and anchor.has_attr('href'):
            href = anchor['href']
            new_link="https://carswitch.com/"+href
            print("newpg",new_link)
        week=weeks_since_published(new_link)
        # week=str(week)
        # date=week_to_date(week=week)
        # obj['available_date']=int(week)
        obj['available_date']=week_to_date(int(week))
        response_new = requests.get(new_link)
        new_soup=BeautifulSoup(response_new.content, "html.parser")
        get_car_name=None
        if new_soup.find('h1') is None:
            continue
        else:
            get_car_name=new_soup.find('h1').text
        print("NAME-------------------------",get_car_name)
        obj['Trim']=get_trim(get_car_name,prefix)
        features_list = new_soup.find('div', class_='features-list')
        location_span = new_soup.find('span', id='location_text')
        # Get the time for which car is in website.
        # script_tag = new_soup.find('script', type='text/javascript')
        # # print("script_tag",script_tag)
        # script_content = script_tag.string if script_tag else ''
        # print("script_content",script_content)

        # Use regex to extract weeks_since_published value
        # match = re.search(r"weeks_since_published:\s*'([^']*)'", script_content)
        # weeks_since_published = match.group(1) if match else None

        # print("weeks",match)
        if location_span:
            print("locationn",location_span.get_text(strip=True))
            obj["City"]=location_span.get_text(strip=True)
        # Find all feature-list__item divs inside the container
        if features_list is None:
            continue
        feature_items = features_list.find_all('div', class_='feature-list__item')
        # Loop through each item and fetch the value from feature-value
        for item in feature_items:
            # transmission = feature_items[9].find('div', class_='feature-value')
            # fuel_type = feature_items[10].find('div', class_='feature-value')
            name_div =item.find('div', class_='feature-name')
            #TRIM
            # get_trim(full_string, prefix)
            # Engine Size
            # if name_div and name_div.get_text(strip=True) == "Engine Size":
            #     value_div = item.find('div', class_='feature-value')
            #     print(value_div.text)
            #     obj["Trim"]=value_div.text
            if name_div and name_div.get_text(strip=True) == "Color":
                value_div = item.find('div', class_='feature-value')
                print(value_div.text)
                obj["Exterior_Color"]=value_div.text
            if name_div and name_div.get_text(strip=True) == "Transmission Type":
                value_div = item.find('div', class_='feature-value')
                print(value_div.text)
                obj["Transmission"]=value_div.text
            if name_div and name_div.get_text(strip=True) == "Fuel Type":
                value_div = item.find('div', class_='feature-value')
                print(value_div.text)
                obj["Fuel"]=value_div.text
            # if name_div and name_div.get_text(strip=True) == "Color":
            #     value_div = item.find('div', class_='feature-value')
            #     print(value_div.text)
            #     obj["Exterior_Color "]=value_div.text
            # if transmission:
            #     print("new_page_data",transmission.get_text(strip=True))
            # if fuel_type:
            #     print("new_page_data",fuel_type.get_text(strip=True))
            obj["seller_type"]="Individual"
            
        create_car_listing = CarListing.objects.create(
            query=car_query_instance,
            image_url=obj.get("Image_URL", ""),
            make=obj.get('Car_Make', ""),
            model= obj.get("Model", ""),
            trim=obj.get("Trim", ""),
            price=obj.get("Price", ""),
            mileage=extract_max_number_from_mileage(obj.get("Kilometers","")),
            currency=obj.get("Currency", ""),  # Added currency field
            city=obj.get("City", ""),
            year=obj.get("Year", ""),
            transmission=obj.get("Transmission", ""),   # Use .get() for safe access
            fuel_type=obj.get("Fuel", ""),              # Use .get() for safe access
            color=obj.get("Exterior_Color", ""),
            vehicle_listing_date=obj.get('available_date', ""),
            vehicle_exit_date=obj.get('release_date', ""),
            seller_type=obj.get('seller_type', ""),
            website="carswitch",
            website_url=new_link
        )
        create_car_listing.save()
        # scraped_data.append(obj)
    # if city is not None:
    #     get_vehicles=get_car_info(make,model,uuid,country,city)
    # else:
    get_vehicles=get_car_info(make,model,uuid)
    return get_vehicles

#GET THE CAR OBJECT
def get_car_info(make,model,uuid):
    get_car=CarListing.objects.filter(make=make,model=model,query_id=uuid)
    return get_car

def get_data_from_carswitch_ksa(request,make,model,uuid,country,city):
    print("In KSA--------------------------------------------------------------------")
    # make="Porsche"
    # make="Porsche"
    # model="Panamera"
    # car_query_instance = CarQuery.objects.get(uuid=uuid)
    # print("car_query_instance",car_query_instance,uuid)
    car_query_instance = CarQuery.objects.get(uuid=uuid)
    print("car_query_instance",car_query_instance)
    if city=="" or city=="All":
        url1 = f"https://ksa.carswitch.com/en/saudi/used-cars/search?keyword={make}%20{model}"
    elif city is not None :
        city=int(city)
        url1=f"https://ksa.carswitch.com/en/saudi/used-cars/search?keyword={make}%20{model}&cities={city}" #WHEN WORKING WITH KSA

    # Step 2: Fetch the page content
    response1 = requests.get(url1)
    prefix = make + " " + model
    soup1 = BeautifulSoup(response1.content, "html.parser")
    car_cards = soup1.find_all("div", class_="card-body")
    image_holders = soup1.find_all(class_=["image-holder"])

    scraped_data = []

    for card, img_holder in zip(car_cards, image_holders):
        # Extract car title or summary
        obj = {}
        year = card.find("span", {"class": "item year"})
        mileage = card.find("span", {"class": "item mileage"})
        price = card.find("span", {"class": "full-price"}).text
        amt= extract_currency_and_amount(price)
        obj['Model'] = model
        obj['Car_Make'] = make
        obj["Year"] = year.text
        # obj['title'] = card.get_text(strip=True)
        obj["title"] = card.find("h2").text
        obj["Currency"] = "SAR"
        obj["Price"] = amt
        # obj["name"]=name.text
        obj["Kilometers"] = mileage.text
        obj['release_date'] = '-'
        obj['listing_period'] = '-'
        obj['seller_type'] = 'Individual'
        # obj[scraper_name]=obj
        # print("title",title)
        # Extract image src
        img_tag = img_holder.find("img")
        # print("img_tag",img_tag)
        img_src = None
        if img_tag:
            img_src = img_tag.get("src") or "https:" + img_tag.get("data-src")
            obj['Image_URL'] = img_src
        #to redirect to href target page
        anchor = img_holder.find('a')
        new_link = None
        if anchor and anchor.has_attr('href'):
            href = anchor['href']
            new_link = "https://ksa.carswitch.com/" + href
            print("newpg", new_link)
        obj['available_date']=weeks_since_published(new_link)             #DURATION of car present here.
        if obj['available_date'] is None:
            continue
        obj['available_date']=week_to_date(int(obj['available_date']))
        response_new = requests.get(new_link)
        new_soup = BeautifulSoup(response_new.content, "html.parser")
        get_car_name=None
        if new_soup.find('h1') is None:
            continue
        else:
            get_car_name=new_soup.find('h1').text
        print("NAME-------------------------", get_car_name)
        obj['Trim']=get_trim(get_car_name,prefix)
        features_list = new_soup.find('div', class_='features-list')
        location_span = new_soup.find('span', id='location_text')
        # Get the time for which car is in website.
        # script_tag = new_soup.find('script', type='text/javascript')
        # # print("script_tag",script_tag)
        # script_content = script_tag.string if script_tag else ''
        # print("script_content",script_content)

        # Use regex to extract weeks_since_published value
        # match = re.search(r"weeks_since_published:\s*'([^']*)'", script_content)
        # weeks_since_published = match.group(1) if match else None

        # print("weeks",match)
        if location_span:
            print("locationn", location_span.get_text(strip=True))
            obj["City"] = location_span.get_text(strip=True)
        if features_list is None:
            continue
        # Find all feature-list__item divs inside the container
        feature_items = features_list.find_all('div', class_='feature-list__item')
        # Loop through each item and fetch the value from feature-value
        for item in feature_items:
            # transmission = feature_items[9].find('div', class_='feature-value')
            # fuel_type = feature_items[10].find('div', class_='feature-value')
            name_div = item.find('div', class_='feature-name')
            #TRIM
            # get_trim(full_string, prefix)
            # Engine Size
            # if name_div and name_div.get_text(strip=True) == "Engine Size":
            #     value_div = item.find('div', class_='feature-value')
            #     print(value_div.text)
            #     obj["Trim"]=value_div.text
            if name_div and name_div.get_text(strip=True) == "Color":
                value_div = item.find('div', class_='feature-value')
                print(value_div.text)
                obj["Exterior_Color"] = value_div.text
            if name_div and name_div.get_text(strip=True) == "Transmission Type":
                value_div = item.find('div', class_='feature-value')
                print(value_div.text)
                obj["Transmission"] = value_div.text
            if name_div and name_div.get_text(strip=True) == "Fuel Type":
                value_div = item.find('div', class_='feature-value')
                print(value_div.text)
                obj["Fuel"] = value_div.text
            # if name_div and name_div.get_text(strip=True) == "Color":
            #     value_div = item.find('div', class_='feature-value')
            #     print(value_div.text)
            #     obj["Exterior_Color "]=value_div.text
            # if transmission:
            #     print("new_page_data",transmission.get_text(strip=True))
            # if fuel_type:
            #     print("new_page_data",fuel_type.get_text(strip=True))
            obj["seller_type"] = "Individual"
        create_car_listing = CarListing.objects.create(
            query=car_query_instance,
            image_url=obj.get("Image_URL", ""),
            make=obj.get('Car_Make', ""),
            model= obj.get("Model", ""),
            trim=obj.get("Trim", ""),
            price=obj.get("Price", ""),
            mileage=extract_max_number_from_mileage(obj.get("Kilometers","")),
            city=obj.get("City", ""),
            year=obj.get("Year", ""),
            currency=obj.get("Currency", ""),  # Added currency field
            transmission=obj.get("Transmission", ""),   # Use .get() for safe access
            fuel_type=obj.get("Fuel", ""),              # Use .get() for safe access
            color=obj.get("Exterior_Color", ""),
            vehicle_listing_date=obj.get('available_date', ""),
            vehicle_exit_date=obj.get('release_date', ""),
            seller_type=obj.get('seller_type', ""),
            website="carswitch",
            website_url=new_link
        )
        create_car_listing.save()
    get_vehicles=get_car_info(make,model,uuid)
    return get_vehicles

def get_data_from_opensooq_uae(request, make=None, model=None,uuid=None,country=None,city=None):
    car_query_instance = CarQuery.objects.get(uuid=uuid)
    if city=="" or city=="All":
        url = f"https://ae.opensooq.com/en/cars?search=true&term={make}+{model}"
    elif city is not None:
        city=int(city)
        city=get_city(city)
        url = f"https://ae.opensooq.com/en/{city}/cars/all?search=true&term={make}+{model}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Get the listing section
    main_div = soup.find("div", id='serpMainContent')

    # Get anchors and corresponding image divs
    anchors = main_div.find_all('a', href=True)
    img_divs = main_div.find_all("div", class_="postImgCont relative radius-8 overflowHidden me-16 grayBg")

    scraped_data = []

    # Loop through anchors and their corresponding image divs (zip safely)
    for a, img_div in zip(anchors, img_divs):
        href = a['href']
        full_url = f"https://ae.opensooq.com{href}"
        print("Visiting:", full_url)

        # Try to extract image URL
        img_tag = img_div.find("img")
        img_url = img_tag.get("data-src") or img_tag.get("src") if img_tag else None
        
        detail_response = requests.get(full_url)
        detail_soup = BeautifulSoup(detail_response.content, "html.parser")
        get_price=detail_soup.find("div",class_="flex alignItems relative priceColor bold font-30 width-fit").text   #priceeee
        get_amt=extract_amount_opensooq(get_price)
        # get_amt=list(get_amt)
        specs_section = detail_soup.find("ul", class_="flex flexSpaceBetween flexWrap mt-8")
        if not specs_section:
            print("No specs section found, skipping...")
            continue

        obj = {}
        all_items = specs_section.find_all("li")

        for item in all_items:
            key = item.find("p", class_="noWrap")
            value = item.find("a") or item.find("span")
            if key and value:
                key_text = key.get_text(strip=True)
                value_text = value.get_text(strip=True)
                # print("key_text:", key_text, "| value_text:", value_text)

                key_map = {
                    "Year": "Year",
                    "Fuel": "Fuel",
                    "Trim": "Trim",
                    "Kilometers": "Kilometers",
                    "Transmission": "Transmission",
                    "Exterior Color": "Exterior_Color",
                    "City": "City",
                    "Car Make": "Car_Make",
                    "Model": "Model",
                }

                if key_text in key_map:
                    obj[key_map[key_text]] = value_text
                

        if obj:
            obj["Listing_URL"] = full_url
            obj["Image_URL"] = img_url
            obj["Currency"] = "AED"  # Default to AED 
            obj["Price"]=get_amt
            obj['available_date']='22.03.2025'
            obj['release_date']='-'
            obj['listing_period']='-'
            obj['seller_type']='Individual'
            print("Extracted:", obj)
            mileage=extract_max_number_from_mileage(obj.get("Kilometers",""))
        create_car_listing=CarListing.objects.create(
            query=car_query_instance,
            image_url=obj["Image_URL"] ,
            make=obj.get('Car_Make', ""),
            model= obj.get("Model", ""),
            trim=obj.get("Trim",""),
            price=obj.get("Price",""),
            mileage=mileage,
            city=obj.get("City",""),
            year=obj.get("Year",""),
            transmission=obj.get("Transmission",""),
            fuel_type=obj.get("Fuel",""),
            color=obj.get("Exterior_Color",""),
            vehicle_listing_date=obj.get('available_date',""),
            vehicle_exit_date=obj.get('release_date',""),
            seller_type="Individual",
            website="opensooq",
            website_url=full_url
        )
        # print("Created-------------------------------------------------",obj["Model"])
        create_car_listing.save()
        scraped_data.append(obj)

    get_vehicles=get_car_info(make,model,uuid)
    return get_vehicles

def get_city(city):
    city=int(city)
    if city==1:
        city="abu-dhabi"
    if city==2:
        city="ajman"
    if city==3:
        city="dubai"
    if city==4:
        city="fujairah"
    if city==5:
        city="ras-al-khaimah"
    if city==6:
        city="sharjah"
    if city==7:
        city="um-al-quwain"
    if city==8:
        city="al-ain"
    if city==9:
        city="al-riyadh"
    if city==10:
        city="jeddah"
    if city==11:
        city="dammam"
    if city==12:
        city="al-khobar"
    if city==13:
        city="mecca"
    if city==14:
        city="al-madinah"
    if city==27:
        city="arar"
    if city==29:
        city="Qasim / Breda"
    if city==33:
        city="tabuk"
    return city

#TO GET THE TIME SINCE WHEN THE CAR IS HERE
def weeks_since_published(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    scripts = soup.find_all("script")

    function_name = "AddToCartPixel"
    target_script = None
    print(target_script)
    for script in scripts:
        # Try inline JS
        script_content = script.get_text()
        if script_content and function_name in script_content:
            target_script = script_content
            break
        # Try external JS
        src = script.get("src")
        if src:
            js_url = src if src.startswith("http") else f"{url}{src}"
            js_response = requests.get(js_url)
            if function_name in js_response.text:
                target_script = js_response.text
                break

    if target_script:
        print("Script containing AddToCartPixel found.")
        match = re.search(r"weeks_since_published\s*:\s*['\"]([^'\"]+)['\"]",
                          target_script)
        if match:
            print("weeks_since_published:", match.group(1))
            return match.group(1)
        else:
            print("weeks_since_published not found in the script.")
            return "None found in the script."
    else:
        print("No script containing AddToCartPixel found.")