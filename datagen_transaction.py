from __future__ import division
import random
import pandas as pd
from pandas import *
import json
import numpy as np
import sys
import datetime
from datetime import timedelta
from datetime import date
import math
from random import sample
from faker import Faker


import profile_weights

def get_user_input():
    # convert date to datetime object
    def convert_date(d):
        for char in ['/', '-', '_', ' ']:
            if char in d:
                d = d.split(char)
                try:
                    return date(int(d[2]), int(d[0]), int(d[1]))
                except:
                    error_msg(3)
        error_msg(3)

    # error handling for CL inputs
    def error_msg(n):
        if n == 1:
            print("Could not open customers file\n")
        elif n == 2:
            print ("Could not open main config json file\n")
        else:
            print ("Invalid date (MM-DD-YYYY)")
        output = "ENTER:\n(1) Customers csv file\n"
        output += "(2) profile json file\n"
        output += "(3) Start date (MM-DD-YYYY)\n"
        output += "(4) End date (MM-DD-YYYY)\n"
        print(output)
        sys.exit(0)

    try:
        customers = open(sys.argv[1], 'r').readlines()
        #customers = open('C:\Users\swarnim\PycharmProjects\data_generation\capstone_data\customers.csv', 'r').readlines()
    except:
        error_msg(1)
    try:
        m = str(sys.argv[2])
        #m = 'C:\Users\swarnim\PycharmProjects\data_generation\profiles\male_30_40_bigger_cities_fruad.json'
        pro = open(m, 'r').read()
        #fix for windows file paths
        pro_name = m.split('profiles')[-1]
        pro_name = pro_name[1:]

    except:
        error_msg(2)
    try:
        startd = convert_date(sys.argv[3])
        #startd = convert_date('01-01-2015')
    except:
        error_msg(3)
    try:
        endd = convert_date(sys.argv[4])
        #endd = convert_date('08-25-2015')
    except:
        error_msg(4)

    return customers, pro, pro_name, startd, endd

def create_header(line):
    headers = line.split('|')
    headers[-1] = headers[-1].replace('\n','')
    headers.extend(['trans_num', 'trans_date', 'trans_time', 'category', 'amt', 'merchant', 'merch_lat', 'merch_long','is_fraud'])
    print(''.join([h + '|' for h in headers])[:-1])
    return headers


class Customer:
    def __init__(self, customer, profile):
        self.customer = customer
        self.attrs = self.clean_line(self.customer)

    def print_trans(self, trans):
        is_traveling = trans[1]
        travel_max = trans[2]
        fraud = trans[0][3]



        for t in trans[0]:

            ## Get transaction location details to generate appropriate merchant record
            cust_state = cust.attrs['state']
            groups = t.split('|')
            trans_cat = groups[3]
            merch_filtered = merch[merch['category'] == trans_cat]
            random_row = merch_filtered.ix[random.sample(list(merch_filtered.index), 1)]
            ##sw added list
            chosen_merchant = random_row.iloc[0]['merchant_name']

            cust_lat = cust.attrs['lat']
            cust_long = cust.attrs['long']


            if is_traveling:
                # hacky math.. assuming ~70 miles per 1 decimal degree of lat/long
                # sorry for being American, you're on your own for kilometers.
                rad = (float(travel_max) / 100) * 1.43

                #geo_coordinate() uses uniform distribution with lower = (center-rad), upper = (center+rad)
                merch_lat = fake.geo_coordinate(center=float(cust_lat),radius=rad)
                merch_long = fake.geo_coordinate(center=float(cust_long),radius=rad)
            else:
                # otherwise not traveling, so use 1 decimial degree (~70mile) radius around home address
                rad = 1
                merch_lat = fake.geo_coordinate(center=float(cust_lat),radius=rad)
                merch_long = fake.geo_coordinate(center=float(cust_long),radius=rad)

            if cust.attrs['profile'] == "male_30_40_smaller_cities.json":
                print(self.customer.replace('\n','') + '|' + t + '|' + str(chosen_merchant) + '|' + str(merch_lat) + '|' + str(merch_long) + '|' + str(fraud))
            else:
                pass
    def clean_line(self, line):
        # separate into a list of attrs
        cols = [c.replace('\n','') for c in line.split('|')]
        # create a dict of name:value for each column
        attrs = {}
        for i in range(len(cols)):
            attrs[headers[i].replace('\n','')] = cols[i].replace('\n','')
        return attrs

if __name__ == '__main__':
    # read user input into Inputs object
    # to prepare the user inputs
    customers, pro, curr_profile, start, end = get_user_input()
    profile = profile_weights.Profile(pro, start, end)

    # takes the customers headers and appends
    # transaction headers and returns/prints
    headers = create_header(customers[0])

    # generate Faker object to calc merchant transaction locations
    fake = Faker()

    # read merchant.csv used for transaction record
    merch = pd.read_csv('demographic_data/merchants.csv' , sep='|')

    # for each customer, if the customer fits this profile
    # generate appropriate number of transactions
    for line in customers[1:]:
        cust = Customer(line, profile)
        if cust.attrs['profile'] == curr_profile:
            cust.print_trans(profile.sample_from())
