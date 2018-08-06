from scrapy import Spider, Request, Selector
from zillow.items import ZillowItem
import sys, time, itertools, re

#total_dict_keys = {}

class ZillowSpider(Spider):
	name = "zillow_spider"
	allowed_urls = ["https://www.zillow.com/"]
	start_urls = ["https://www.zillow.com/"]


	def parse(self, resposne):

		# -a "#####" to add zipcode on terminal
		# self.zipcode for command line argument
		zipcode = ["10918"] 

		# Add zip code to URL from Command line arguments
		add_zip_urls = ["https://www.zillow.com/homes/for_sale/{}/priced_sort/1_mmm/1_fr/".format(x) for x in zipcode]
		recent_sold_addZipUrls = add_zip_urls.copy()

		# Add page numbers 1-6, for 'for_sale' houses. Changes per zipcode
		result_urls = []
		for i in range(0,len(add_zip_urls)):
			for x in range(1,7):
				result_urls.append(str(add_zip_urls[i]) + "{}_p/".format(x))


		# Change /for_sale/ to /recently_sold/ and add page numbers 1-20
		for i in range(0,len(recent_sold_addZipUrls)):
			for x in range(1,21):
				result_urls.append(str(recent_sold_addZipUrls[i]).replace('for_sale','recently_sold').replace("1_mmm/1_fr/",'') + "{}_p/".format(x))

		for url in result_urls:
			time.sleep(1)
			yield Request(url=url, callback=self.parse_for_house_links)


	def parse_for_house_links(self, response):
		time.sleep(3)

		# Each individual houses URL extentions
		house_extentions = ["https://www.zillow.com/{}?fullpage=true".format(x) for x in response.xpath('//li/article/div/a/@href').extract()]
		#test_house_extentions = ["https://www.zillow.com/homedetails/481-Bull-Mill-Rd-Chester-NY-10918/66499833_zpid/?fullpage=true"]
		
		for url in house_extentions:
			yield Request(url=url, callback=self.parse_for_house_info)


	def parse_for_house_info(self, response):
		time.sleep(1)

		## Testing number of facts and features
		# global total_dict_keys

		#Creating Dict for fact and feature keys
		output = {}

		#Selects all fact and feature containers
		sel = Selector(response=response).xpath('.//div[@class="hdp-fact-container"]')
		

		## for each container, for example: 
		# type_name = Dates
		# category_name = 'date_built'
		# category_value =  1970
		for i in sel:

			type_name      = i.xpath('./div[@class="hdp-fact-category"]/text()').extract()
			category_name  = i.xpath('./ul/li/span[@class="hdp-fact-name"]/text()').extract()
			category_value = i.xpath('./ul/li/span[@class="hdp-fact-value"]/text()').extract()

			# if no category_name, assign type_name
			if (len(category_name) != len(category_value)):
				category_name = type_name + category_name

			# zip items together into dict, so that all tuples have same number of elements
			# combine into single dict per page: output
			a = dict(itertools.zip_longest(category_name,category_value))
			output = {**output, **a} 
			#total_dict_keys = {**total_dict_keys, **output}
			
		#print(len(total_dict_keys.keys()),total_dict_keys.keys())
		# Address
		address = ''.join(response.xpath('//h1[@class="notranslate"]//text()').extract()[:2])


		## Check for home status
		# Homes for sale / forclosure / auction
		if (response.xpath('//div[@class="zsg-lg-1-3 zsg-md-1-1 hdp-summary"]/div[@id="home-value-wrapper"]/div/div[@class=" status-icon-row for-sale-row home-summary-row"]/text()').extract() != []):


			if(response.xpath('//span[@class="zsg-tooltip-launch zsg-tooltip-launch_keyword"]/text()').extract_first() == "Foreclosure"):
				home_status = response.xpath('//span[@class="zsg-tooltip-launch zsg-tooltip-launch_keyword"]/text()').extract_first()
			elif( response.xpath('//span[@class="zsg-tooltip-launch zsg-tooltip-launch_keyword"]/text()').extract_first() == "Auction"):
				home_status = response.xpath('//span[@class="zsg-tooltip-launch zsg-tooltip-launch_keyword"]/text()').extract_first()
			else:
				home_status = response.xpath('//div[@class="zsg-lg-1-3 zsg-md-1-1 hdp-summary"]/div[@id="home-value-wrapper"]/div/div[@class=" status-icon-row for-sale-row home-summary-row"]/text()').extract()[1].strip()


		# Homes for rent
		elif any("Rent" in s for s in response.xpath('//span[@class="zsg-tooltip-launch zsg-tooltip-launch_keyword"]/text()').extract()):
				home_status = response.xpath('//div[@class=" status-icon-row for-rent-row home-summary-row"]/text()').extract()[1].strip()


		# Home that are sold
		elif any("Sold" in s for s in response.xpath('//div[@class="main-row status-icon-row recently-sold-row home-summary-row"]/text()').extract()):
				home_status = response.xpath('//div[@class="main-row status-icon-row recently-sold-row home-summary-row"]/text()').extract()[1].strip().replace(":",'')

		# Homes about to be forclosed on or "Make Me Moves"
		else:
			home_status = response.xpath('//span[@class="zsg-tooltip-launch zsg-tooltip-launch_keyword"]/text()').extract_first()


		## Check for Sale Price and Zestimate, each home_status stores it differently
		if(home_status == "Foreclosed"):
			sale_price = response.xpath('//div[@class="  home-summary-row"]/span[@class=""]/text()').extract_first().strip()
			if(response.xpath('//div[@class="  home-summary-row"]/span[@data-target-id="below-zest-tip-hdp"]/text()').extract_first()[:5]=='Below'):
				zestimate = response.xpath('//div[@class="  home-summary-row"]/span[@class=""]/text()').extract_first().strip()
				zestimate = zestimate.replace(',','').replace('$','')
				add = response.xpath('//div[@class="  home-summary-row"]/span[@class=""]/text()').extract()[1].strip()
				add = add[:4].replace('$','')
				add = int(add) * 1000
				zestimate = str("$"+str(int(zestimate)+ int(add)))

		elif(home_status == 'Make Me Move'):
			sale_price = response.xpath('//div[@class="main-row  home-summary-row"]/span/text()').extract_first().strip()
			zestimate = response.xpath('//div[@class="  home-summary-row"]/span[@class=""]/text()').extract_first().strip()

		elif(home_status == 'For Rent'):
			sale_price = response.xpath('//div[@class="main-row  home-summary-row"]/span/text()').extract_first().strip()
			zestimate = response.xpath('//div[@class="  home-summary-row"]/span[@class=""]/text()').extract_first().strip()

		elif(home_status == 'Auction'):
			sale_price = "NaN"
			zestimate = response.xpath('//div[@class="  home-summary-row"]/span/text()').extract()[1].strip()

		elif(home_status == 'Sold'):
			sale_price = response.xpath('//div[@class="main-row status-icon-row recently-sold-row home-summary-row"]/span/text()').extract_first().strip()
			if (len(response.xpath('//div[@class="  home-summary-row"]/span[@class=""]/text()').extract()) > 1):
				zestimate = response.xpath('//div[@class="  home-summary-row"]/span[@class=""]/text()').extract()[1].strip()
			else:
				zestimate = "NaN"

		else:
			sale_price = response.xpath('//div[@class="zsg-lg-1-3 zsg-md-1-1 hdp-summary"]/div[@id="home-value-wrapper"]/div/div[2]/span/text()').extract_first()
			zestimate = response.xpath('//div[@class="zsg-lg-1-3 zsg-md-1-1 hdp-summary"]/div[@id="home-value-wrapper"]/div/div[3]/span[2]/text()').extract_first()

		# if Zestimate is stored behind Javascript, just put NaN. too many captchas!!!!
		if (zestimate != None):
			if (zestimate.replace(',','').replace('$','').strip().isdigit()):
				pass
			else:
				zestimate = "NaN"
		else:
				zestimate = "NaN"


		## Begin Adding values to correct variables and assign to ZillowItem()
		# Not every zillow page has every value, check for each, if not there: "NaN"
		# Some values are written differently per page, ex: Elementary school & grade school,
		#   the if statements below handle which one is there

		house = ZillowItem()
		# Top Bold
		house['address'] = address
		house['home_status'] = home_status
		house['sale_price'] = sale_price
		house['zestimate'] = zestimate

		#######################
		#### Facts and Features
		#######################

		## Interior Features
		#######################
		output.setdefault('Beds: ', "NaN")
		output.setdefault('Baths: ', "NaN")
		if (output['Beds: '] == "NaN"):
			if (response.xpath('//meta[@property="zillow_fb:beds"]/@content').extract_first() != None):
				output['Beds: '] = response.xpath('//meta[@property="zillow_fb:beds"]/@content').extract_first()
		if (response.xpath('//meta[@property="zillow_fb:baths"]/@content').extract_first() != None):
			output['Baths: '] = response.xpath('//meta[@property="zillow_fb:baths"]/@content').extract_first()

		output.setdefault('Heating: ', "NaN")
		output.setdefault('Cooling: ', "NaN")
		output.setdefault('Attic Description: ', "NaN")
		output.setdefault('Appliances included: ', "NaN")
		output.setdefault('Floor size: ', "NaN")
		output.setdefault('Flooring: ', "NaN")
		output.setdefault('Other Interior Features', "NaN")
		output.setdefault('Basement', "NaN")
		output.setdefault('Basement Description: ', "NaN")
		output.setdefault('Room count: ', "NaN")

		bedrooms  = output['Beds: ']
		bathrooms = output['Baths: ']
		heating = output['Heating: ']
		cooling = output['Cooling: ']
		attic = output['Attic Description: ']
		appliances = output['Appliances included: ']
		floor_sqft = output['Floor size: ']
		floor_type = output['Flooring: ']
		other_int_features = output['Other Interior Features']
		basement = output['Basement']
		basement_desc = output['Basement Description: ']
		room_count =output['Room count: ']

		house['bedrooms'] = bedrooms
		house['bathrooms'] = bathrooms
		house['heating'] = heating
		house['cooling'] = cooling
		house['attic'] = attic
		house['appliances'] = appliances
		house['floor_sqft'] = floor_sqft
		house['floor_type'] = floor_type
		house['other_int_features'] = other_int_features
		house['basement'] = basement
		house['basement_desc'] = basement_desc
		house['room_count'] = room_count

		## Building
		# 


		## Spaces and Amenities
		#######################
		output.setdefault('Spaces', "NaN")
		if ('Amenities' in output):
			output.setdefault('Amenities', "NaN")
		elif ('AMENITIES: ' in output):
			output.setdefault('AMENITIES: ', "NaN")
		else:
			output.setdefault('Amenities: ', "NaN")

		spaces = output['Spaces']
		if ('Amenities' in output):
			amenities = output['Amenities']
		elif ('AMENITIES: ' in output):
			amenities = output['AMENITIES: ']
		else:
			amenities = output['Amenities: ']
		



		house['spaces'] = spaces
		house['amenities'] = amenities

		## Construction
		#######################
		output.setdefault('Structure type: ', "NaN")
		output.setdefault('Type and Style', "NaN")
		output.setdefault('Exterior material: ', "NaN")
		output.setdefault('Siding Description: ', "NaN")
		output.setdefault('Construction Description: ', "NaN")
		output.setdefault('Dates', "NaN")
		output.setdefault('Year Built Exception: ', "NaN")
		if ('Roof type: ' in output):
			output.setdefault('Roof type: ', "NaN")
		else:
			output.setdefault('roof_types: ', "NaN")
		output.setdefault('Last remodel year: ', "NaN")
		output.setdefault('Stories: ', "NaN")
		output.setdefault('architectural_style: ', "NaN")

		structure_type = output['Structure type: ']
		num_families = output['Type and Style']
		exterior_material = output['Exterior material: ']
		siding_desc = output['Siding Description: ']
		constuct_desc = output['Construction Description: ']
		date_built = output['Dates']
		date_built_exception = output['Year Built Exception: ']
		if ('Roof type: ' in output):
			roof_type = output['Roof type: ']
		else:
			roof_type = output['roof_types: ']
		last_remodel = output['Last remodel year: ']
		stories = output['Stories: ']
		architec_style = output['architectural_style: ']

		house['structure_type'] = structure_type
		house['num_families'] = num_families
		house['exterior_material'] = exterior_material
		house['siding_desc'] = siding_desc
		house['constuct_desc'] = constuct_desc
		house['date_built'] = date_built
		house['date_built_exception'] = date_built_exception
		house['roof_type'] = roof_type
		house['last_remodel'] = last_remodel
		house['stories'] = stories
		house['architec_style'] = architec_style

		## Exterior Features
		#######################
		output.setdefault('Water Description: ', "NaN")
		output.setdefault('Lot: ', "NaN")
		if('Lot Description: ' in output):
			output.setdefault('Lot Description: ', "NaN")
		else:
			output.setdefault('LOT DESC: ', "NaN")
		output.setdefault('Patio', "NaN")
		output.setdefault('Yard', "NaN")
		output.setdefault('Water', "NaN")
		output.setdefault('View: ', "NaN")
		if ('Other Exterior Features' in output):
			output.setdefault('Other Exterior Features', "NaN")
		elif('EXTERIOR FEATURES: ' in output):
			output.setdefault('EXTERIOR FEATURES: ', "NaN")
		else:
			output.setdefault('exterior_features_desc:', "NaN")
		


		water_desc = output['Water Description: ']
		lot_size = output['Lot: ']
		if('Lot Description: ' in output):
			lot_desc = output['Lot Description: ']
		else:
			lot_desc = output['LOT DESC: ']
		patio = output['Patio']
		yard = output['Yard']
		water = output['Water']
		view = output['View: ']
		if ('Other Exterior Features' in output):
			other_ext_features = output['Other Exterior Features']
		elif('EXTERIOR FEATURES: ' in output):
			other_ext_features = output['EXTERIOR FEATURES: ']
		else:
			other_ext_features = output['exterior_features_desc:']



		house['water_desc'] = water_desc
		house['lot_size'] = lot_size
		house['lot_desc'] = lot_desc
		house['patio'] = patio
		house['yard'] = yard
		house['water'] = water
		house['view'] = view
		house['other_ext_features'] = other_ext_features

		## Community and Neighborhood
		#######################
		if ('Elementary school: ' in output):
			output.setdefault('Elementary school: ', "NaN")
		else:
			output.setdefault('grade_school: ', "NaN")
		output.setdefault('Middle school: ', "NaN")
		output.setdefault('High school: ', "NaN")
		output.setdefault('School district: ', "NaN")
		if ('Transportation' in output):
			output.setdefault('Transportation', "NaN")
		else:
			output.setdefault('Road Front Description: ', "NaN")


		if ('Elementary school: ' in output):
			Elementary_s = output['Elementary school: ']
		else:
			Elementary_s = output['grade_school: ']
		Middle_s = output['Middle school: ']
		High_s = output['High school: ']
		s_district = output['School district: ']
		if ('Transportation' in output):
			transport = output['Transportation']
		else:
			transport = output['Road Front Description: ']

		house['Elementary_s'] = Elementary_s
		house['Middle_s'] = Middle_s
		house['High_s'] = High_s
		house['s_district'] = s_district
		house['transport'] = transport

		## Parking
		#######################
		output.setdefault('Parking: ', "NaN")

		parking = output['Parking: ']

		house['parking'] = parking

		## Utilities
		#######################
		if ('Garbage: ' in output):
			output.setdefault('Garbage: ', "NaN")
		else:
			output.setdefault('garbage', "NaN")
		output.setdefault('Hotwater: ', "NaN")
		output.setdefault('Sewer Description: ', "NaN")
		output.setdefault('Green Energy', "NaN")

		if ('Garbage: ' in output):
			garbage = output['Garbage: ']
		else:
			garbage = output['garbage']
		hotwater = output['Hotwater: ']
		sewer_desc = output['Sewer Description: ']
		green_energy = output['Green Energy']

		house['garbage'] = garbage
		house['hotwater'] = hotwater
		house['sewer_desc'] = sewer_desc
		house['green_energy'] = green_energy

		## Finance
		#######################
		output.setdefault('Tax Source: ', "NaN")
		output.setdefault('Tax Amount: ', "NaN")
		output.setdefault('Tax Year: ', "NaN")

		tax_source = output['Tax Source: ']
		tax_amount = output['Tax Amount: ']
		tax_year = output['Tax Year: ']

		house['tax_source'] = tax_source
		house['tax_amount'] = tax_amount
		house['tax_year'] = tax_year

		## Other
		#######################
		output.setdefault('Last sold: ', "NaN")
		if ('Price/sqft: ' in output):
			output.setdefault('Price/sqft: ', "NaN")
		else:
			output.setdefault('Last sale price/sqft: ', "NaN")
		output.setdefault('Property Type: ', "NaN")
		output.setdefault('Post Office: ', "NaN")
		

		if (output['Last sold: '] == "Disability Access"):
			if ('Price/sqft: ' in output):
				output['Price/sqft: '] = output['Property Type: ']
				output['Last sold: '] = "NaN"
				output['Property Type: '] = "NaN"
			else:
				output['Last sale price/sqft: '] = output['Property Type: ']
				output['Last sold: '] = "NaN"
				output['Property Type: '] = "NaN"
			
		elif(output['Last sold: '] == "Mother-in-Law Apartment"):
			if ('Price/sqft: ' in output):
				output['Last sold: '] = output['Price/sqft: ']
				output['Price/sqft: '] = output['Property Type: ']
				output['Property Type: '] = "NaN"
			else:
				output['Last sold: '] = output['Last sale price/sqft: ']
				output['Last sale price/sqft: '] = output['Property Type: ']
				output['Property Type: '] = "NaN"
		
		last_sold = output['Last sold: ']		
		if ('Price/sqft: ' in output):
			price_per_sqft = output['Price/sqft: ']
		else:
			price_per_sqft = output['Last sale price/sqft: ']
		prop_type = output['Property Type: ']
		post_office = output['Post Office: ']

		house['last_sold'] = last_sold
		house['price_per_sqft'] = price_per_sqft
		house['prop_type'] = prop_type
		house['post_office'] = post_office


		# Activity on Zillow
		# '', '', None (# saved this home)
		output.setdefault('Days on Zillow: ', "NaN")
		if ('Views in the past 30 days: ' in output):
			output.setdefault('Views in the past 30 days: ', "NaN")
		else:
			output.setdefault('Views since listing: ', "NaN")
		
		days_on_zillow = output['Days on Zillow: ']
		if ('Views in the past 30 days: ' in output):
			views_in_last_30_days = output['Views in the past 30 days: ']
		else:
			views_in_last_30_days = output['Views since listing: ']

		house['days_on_zillow'] = days_on_zillow
		house['views_in_last_30_days'] = views_in_last_30_days
		


		yield(house)


##############
## From 10918 zip, all facts and features.  Only using 56 above
##############
# 183 dict_keys(['Beds: ', 'Baths: ', 'Heating: ', 'Cooling: ', 'Attic Description: ', 'Appliances included: ',
# 'Floor size: ', 'Flooring: ', 'Other Interior Features', 'Sq Ft Source: ', 'Amenities: ', 'Type and Style', 
# 'Structure type: ', 'Siding Description: ', 'Construction Description: ', 'Dates', 'Year Built Exception: ', 
# 'Patio', 'Water Description: ', 'Lot: ', 'Lot Description: ', 'Parcel #: ', 'Hamlet: ', 'Elementary school: ', 
# 'Middle school: ', 'High school: ', 'School district: ', 'Parking: ', 'Garbage: ', 'Hotwater: ', 'Sewer Description: ', 
# 'Tax Source: ', 'Tax Amount: ', 'Tax Year: ', 'MLS #: ', 'Price/sqft: ', 'Property Type: ', 'Status: ', 'Post Office: ',
# 'Included: ', 'Days on Zillow: ', 'Views in the past 30 days: ', None, 'Basement', 'Attic', 'Room count: ',
# 'Spaces', 'Amenities', 'Materials', 'Roof type: ', 'Exterior material: ', 'Stories: ', 'Yard', 'View: ',
# 'Neighborhood name: ', 'Green Energy', 'Last sold: ', 'Heating Type: ', 'central_air_desc: ', 'heating_desc: ',
# 'roof_types: ', 'architectural_style: ', 'Other Exterior Features', 'grade_school: ', 'parking: ', 'taxes_annual: ',
# 'original_listhub_key: ', 'Views since listing: ', 'Unit count: ', 'Last remodel year: ', 'Style: ', 'Water', 'Village: ',
# 'Laundry: ', 'Pets: ', 'Posted: ', 'Rent/sqft: ', 'HOA Fee: ', 'Air Conditioning: ', 'Lot width: ', 'Lot depth: ', 'Attic size: ',
# 'Addition size: ', 'Heating Fuel: ', 'Basement Description: ', 'Last sale price/sqft: ', 'Sewer Type: ', 'Water Source Type: ',
# 'HOA or Building Fee: ', 'Has Central AC: ', 'HEATING: ', 'INTERIOR FEATURES: ', 'Type: ', 'Sub Type: ', 'CONSTRUCTION: ',
# 'FOUNDATION: ', 'LOT DESC: ', 'EXTERIOR FEATURES: ', 'EXTERIOR: ', 'PARK/GARAGE: ', 'WATER/SEWER: ', 'ELECTRICITY: ',
# 'Square Ft Source: ', 'LOCK BOX DESCRIPTION: ', 'EQUIPMENT: ', 'Foundation type: ', 'Typeof Unit: ', 'Hoa Fee Includes: ',
# 'Utilities Included: ', 'dining_rooms: ', 'living_rooms: ', 'fireplaces: ', 'Features: ', 'Utilities On Abutting Site: ',
# 'Road Front Description: ', 'Available Utilities: ', 'Transportation', 'MBR 1ST FLOOR: ', 'Eat In Kitchen: ', '# Kitchens: ',
# 'Den/Family Room: ', 'Office: ', 'A/C: ', 'Heat: ', 'Fuel: ', 'Washer: ', 'W/W Carpet: ', 'Wood Floors: ', 'Detached/Attached: ',
# 'Driveway: ', 'Water: ', 'County: ', 'Sewer: ', 'Picture: ', 'Zone: ', 'Family  Room: ', 'Construction Type: ', 'View Wooded: ',
# 'View Street: ', 'Add Fee Frequency: ', 'Additional Fee Des: ', 'Additional Fees Amt: ', 'Entry Foyer: ', 'Room 1 Level: ',
# 'Room 2 Level: ', 'Room 3 Level: ', 'Room 4 Level: ', 'Room 5 Level: ', 'Room 4: ', 'Room 1: ', 'Room 5: ', 'OTHER ROOMS: ',
# 'Room 6 Level: ', 'Room 7 Level: ', 'Room 6: ', 'Room 8 Level: ', 'Room 11 Level: ', 'Room 10 Level: ', 'Room 9 Level: ', 'Room 7: ',
# 'Room 2: ', 'Room 9: ', 'Room 11: ', 'Room 8: ', 'Room 10: ', 'has_lawn_fl: ', 'exterior_features_desc: ', 'Residential Style: ',
# 'Soil Type: ', 'Room 3: ', 'BASEMENT: ', 'AMENITIES: ', 'Unit floor #: ', 'End Unit: ', 'Pets Allowed: ', 'has_pond_fl: ', 'neighborhoods: ',
# 'has_security_system_fl: ', 'Appliance Oven: ', 'Building Style: ', 'Short Sale Y/N: ', 'viewpoints: ', 'Bonus Room: '])