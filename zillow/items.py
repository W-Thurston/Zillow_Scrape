# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZillowItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    
    # Top Bold
    address = scrapy.Field()
    home_status = scrapy.Field()
    sale_price = scrapy.Field()
    zestimate = scrapy.Field()

    # Facts and Features

    # Interior Features
    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()
    heating = scrapy.Field()
    cooling = scrapy.Field()
    attic = scrapy.Field()
    appliances = scrapy.Field()
    floor_sqft = scrapy.Field()
    floor_type = scrapy.Field()
    other_int_features = scrapy.Field()
    basement = scrapy.Field()
    basement_desc = scrapy.Field()
    room_count = scrapy.Field()

    # Building

    ## Spaces and Amenities
    # 'Spaces', 'Amenities',
    spaces    = scrapy.Field()
    amenities = scrapy.Field()

    # Construction
    structure_type = scrapy.Field()
    num_families = scrapy.Field()
    exterior_material = scrapy.Field()
    siding_desc = scrapy.Field()
    constuct_desc = scrapy.Field()
    date_built = scrapy.Field()
    date_built_exception = scrapy.Field()
    roof_type = scrapy.Field()
    last_remodel = scrapy.Field()
    stories = scrapy.Field()
    architec_style = scrapy.Field()

    # Exterior Features
    water_desc = scrapy.Field()
    lot_size = scrapy.Field()
    lot_desc = scrapy.Field()
    patio = scrapy.Field()
    yard = scrapy.Field()
    water = scrapy.Field()
    view = scrapy.Field()
    other_ext_features = scrapy.Field()

    # Community and Neighborhood
    Elementary_s = scrapy.Field()
    Middle_s     = scrapy.Field()
    High_s       = scrapy.Field()
    s_district   = scrapy.Field()
    transport    = scrapy.Field()

    # Parking
    parking = scrapy.Field()

    # Utilities
    garbage = scrapy.Field()
    hotwater = scrapy.Field()
    sewer_desc = scrapy.Field()
    green_energy = scrapy.Field()

    # Finance
    tax_source = scrapy.Field()
    tax_amount = scrapy.Field()
    tax_year = scrapy.Field()

    # Other
    last_sold = scrapy.Field()
    price_per_sqft = scrapy.Field()
    prop_type = scrapy.Field()
    post_office = scrapy.Field()

    # Activity on Zillow
    days_on_zillow = scrapy.Field()
    views_in_last_30_days = scrapy.Field()
    num_of_saves = scrapy.Field()



    


