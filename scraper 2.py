from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
from random import randrange

#link_to_first_page = "https://www.bezrealitky.com/listings/offer-rent/flat?project%5B0%5D=0&_token=sNkxU4c86ySwxmwZtp-rVa20UIPPToucYNR20Sc1UIM&submit=1&page=".format(page)
bezrealitky_link_base = "https://www.bezrealitky.com"

# read the csv that stores the structure of the data as we need it
csv_flats = pd.read_csv(r"Flats_base_structure.csv", sep = ";")

# covert the csv in pandas dataframe

base_data_frame = pd.DataFrame(csv_flats)

# open the file with our stored data, and read only the line with column ID, to avoid to read unuseful data, this will be the base for check if flat is already listed

flat_ID_in_csv = pd.read_csv(r"flats_data.csv", sep = ";", usecols = [0])

print(csv_flats)

print(flat_ID_in_csv)

#in range choose the number of page to iterate in case of need to start from last page range(100, 0, -1)
for page in range(1, 10):

    link_to_first_page = "https://www.bezrealitky.com/listings/offer-rent/flat?project%5B0%5D=0&_token=sNkxU4c86ySwxmwZtp-rVa20UIPPToucYNR20Sc1UIM&submit=1&page="+f"{page}"

    #request to get the text of page form Bezrealitky, wiht preagreed settings of research (prague flats only), might be changed in future to get more data
    html_text = requests.get(link_to_first_page).text

    soup = BeautifulSoup(html_text, "lxml")

    #in the html text of the selected page, search all flats listed in the page
    flats = soup.find_all("div", class_ = "product__body-new")

    for flat in flats:

        price = flat.find_all(class_ = "product__value")
        link_test = flat.find("a", class_ = "product__link js-product-link")
        link = flat.div.h3.a["href"]
        link_completed = f"{bezrealitky_link_base}"+ f"{link}"
        print(link_completed)

        #we try now to access the page of the single flat for more details

        flat_page_html = requests.get(link_completed).text
        flat_page = BeautifulSoup(flat_page_html, "lxml")

        # get listing_id from page, split methon divedes the string in elemnts accordinf to parameter given and create list (that will be added to dict later)

        flat_listing = flat_page.find("div", class_ = "col text-right align-self-center d-none d-lg-block").get_text().strip()
        listing_list = flat_listing.split(": ")

        # get street, town and district

        flat_location = flat_page.find("h2").get_text().strip()
        flat_location_cleaning = flat_location.replace(" -", ",")
        flat_location_list = flat_location_cleaning.split(", ")

        # define a list of keys to use to append lcation data to dictionary
        flat_location_keys = ["Street", "Town", "Metropolitan_district"]

        #in specifications we get the part of the page with specifications as the data we need
        #the data is divided in parameters and value (with different tags), so we create 2 list that we will iterate to get single values

        specifications = flat_page.find("div", class_ = "detail-box pr-30 mb-20")
        parameters = specifications.find_all("div", class_ = "col col-6 param-title")
        parameters_values = specifications.find_all("div", class_ = "col col-6 param-value")

        #create a dictionary to store the linked info of each flat
        flat_available_info = {}

        flat_available_info = dict([listing_list])

        flat_available_info["Listing_ID"] = flat_available_info["Listing ID"]
        del flat_available_info["Listing ID"]

        flat_available_info.update(zip(flat_location_keys, flat_location_list))

        #get text method allows to get the data we need as text, strip method allows to get rid of the not needed blak spaces
        # add to the dict the paired valus for the 2 list, so each dict created has all the ifo for the flat
        # replace method allow to remove spaces between multiple words in parameters and add an underscore, making it better for storgae
        for parameter, value in zip(parameters, parameters_values):
            flat_available_info[parameter.get_text().strip().replace(" ", "_")] = value.get_text().strip()

        print("this is the full info available")
        print(flat_available_info)

        flat_ID = flat_available_info["Listing_ID"]

        # we check if the flat_id is already in the dataframe, that we previously created with only ID column
        # it's important to use .vlaues to get only the values and .astype(str) because to have the data from dataframe as string, as the element used for comparison from dict is a string
        # if value is not in dataframe code will be executed, if itàs there it will move to next item

        if flat_ID not in flat_ID_in_csv.values.astype(str):

            # create a dataframe in pandas using the scraped data for the single flat

            scraped_data_frame = pd.DataFrame(data = flat_available_info, index = [0])

            combined_data = pd.concat([base_data_frame, scraped_data_frame], sort = False, keys = scraped_data_frame)

            print(combined_data)

            combined_data.to_csv(r"flats_data.csv", mode = "a", sep=";", header = False, index = False)

            time.sleep(randrange(3))

        else:

            print("already in csv, not adding this one...")
            print("we scraped evrything we needed...")
            print("csv complete")
            #exit()


    time.sleep(10)
