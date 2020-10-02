from django.shortcuts import render
from django.http import JsonResponse
from bson import BSON
import pymongo
import pandas
import json
import ssl


MONGO_PROJECTION = {
    "_id": 0,
    "name": 1,
    "cuisine": 1,
    "address.street": 1,
    "borough": 1,

}

# Create your views here.
def home(request):
    return render(request, 'home.html', {})

def about(request):
    return render(request, 'about.html', {})

def search_params(request):

    if request.method == "POST":
        street = request.POST['street']
        county = request.POST['county']
        zipcode = request.POST['zipcode']
        name = request.POST['name']
        cuisine = request.POST['cuisine']
        limit = request.POST['result-num']

        search_fields = {
            "street": street,
            "county": county,
            "zipcode": zipcode,
            "name": name,
            "cuisine": cuisine,
            "limit": limit
        }

        return search_fields

def create_mongo_query(request):
    search_fields = search_params(request)

    if search_fields is None:
        mongo_query = {}
        result_limit = 100
        return mongo_query, result_limit

    else:

    # Create empty string variables
        street_string = ""
        county_string = ""
        zipcode_string = ""
        name_string = ""
        cuisine_string = ""
        mongo_query = ""
        result_limit = 100

        # Check if search_fields are populated and construct mongodb query strings
        if (search_fields["limit"]):
         result_limit = int(search_fields["limit"])

        if (search_fields["street"]):
            street_string = '"address.street": {$regex: "' + str(search_fields["street"]) + '"},'

        if (search_fields["county"]):
            county_string = '"borough": {$regex: "' + str(search_fields["county"]) + '"},'

        if (search_fields["zipcode"]):
            zipcode_string = '"address.zipcode": {$regex: "' + str(search_fields["zipcode"]) + '"},'

        if (search_fields["name"]):
            name_string = '"name": {$regex: "' + str(search_fields["name"]) + '"},'

        if (search_fields["cuisine"]):
            cuisine_string = '"cuisine": {$regex: "' + str(search_fields["cuisine"]) + '"},'

        # Put together string variables separated by commas
        mongo_query = street_string + county_string + zipcode_string + name_string + cuisine_string
        #mongo_query = BSON.encode({mongo_query})

        return mongo_query, result_limit

def get_mongo_data(request):
    query_info = create_mongo_query(request)
    result_limit = query_info[1]
    mongo_string = query_info[0]
    #mongo_string = mongo_string.replace("'","")

    #check if query_info is empty
    #if (mongo_string):
    #    mongo_string = query_info[0]

    myClient = pymongo.MongoClient("mongodb+srv://ecUser:HahaGGjgDiff@free-cluster-py.ptij8.mongodb.net/sample_analytics?retryWrites=true&w=majority", ssl=True, ssl_cert_reqs=ssl.CERT_NONE)
    #put user input into query
    myDb = myClient["sample_restaurants"]
    myCol = myDb["restaurants"]
    results = myCol.find({},MONGO_PROJECTION).limit(result_limit)
    return results

def restaurants(request):

    #Pull data from mongodb and set to pandas df
    query_info = create_mongo_query(request)
    json_data = get_mongo_data(request)
    df = pandas.DataFrame.from_dict(json_data, orient='columns')
    df_html = df.to_html

    # Create dictionary for template
    input_copy = {
        "df": df_html,
        "query_string": query_info[0],
        "result_num": query_info[1],
    }

    return render(request, 'restaurants.html', input_copy)
