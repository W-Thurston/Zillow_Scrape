import sys

if (len(sys.argv) >= 2):
	zipcode = list(sys.argv)[1:]
else:
	zipcode = str(input("Zipcode: ")).split(' ')



print(list(sys.argv)[1:])

add_zip_urls = ["https://www.zillow.com/homes/for_sale/{}/priced_sort/1_mmm/1_fr/".format(x) for x in zipcode]
recent_sold_addZipUrls = add_zip_urls.copy()

start_urls = []
for i in range(0,len(add_zip_urls)):
	for x in range(2,5):
		start_urls.append(str(add_zip_urls[i]) + "{}_p/".format(x))

# for i in temp:
# 	print(i)


for i in range(0,len(recent_sold_addZipUrls)):
	for x in range(10,15):
		start_urls.append(str(recent_sold_addZipUrls[i]).replace('for_sale','recently_sold').replace("1_mmm/1_fr/",'') + "{}_p/".format(x))

for i in start_urls:
	print(i)

