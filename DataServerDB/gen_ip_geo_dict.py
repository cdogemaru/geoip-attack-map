import geoip2.database
import ipaddress
import maxminddb
import numpy as np
import csv
import pickle as pkl
city_path = '../DataServerDB/GeoLite2-City.mmdb'
asn_path = '../DataServerDB/GeoLite2-ASN-Blocks-IPv4.csv'

# asnreader = geoip2.database.Reader(asn_path)
cityreader = maxminddb.open_database(city_path)

geo_dict = {}

with open(asn_path, "r") as f:
    csvreader = csv.reader(f)
    # jump the header line
    csvreader.__next__()

    cnt = 0

    for line in csvreader:
        cnt += 1
        if cnt % 1000 == 0:
            print(cnt)
        (network_str, asn, company) = line
        network = ipaddress.ip_network(network_str)
        rand_hosts = []
        for i in network.hosts():
            rand = np.random.uniform(0,1)
            if rand > 0.05:
                rand_hosts.append(i)
            if len(rand_hosts) > 50:
                break

        geos = []
        for host in rand_hosts:
            response = cityreader.get(host)
            if response and "location" in response and "registered_country" in response:
                location = response["location"]
                long = location["longitude"]
                lati = location["latitude"]

                country_name = response["registered_country"]["names"]["en"]
                country_code = response["registered_country"]["iso_code"]

                # print(country_name, country_code)

                geos.append((long, lati, country_name, country_code))

        geos = list(set(geos))
        if not asn in geo_dict:
            geo_dict[asn] = geos
        else:
            old_geos = geo_dict[asn]
            # print(old_geos)
            geos.extend(old_geos)
            geos = list(set(geos))
            geo_dict[asn] = geos

# print(geo_dict)

with open("./ASN_GEO_DICT.pkl", "wb") as f:
    pkl.dump(geo_dict, f)
