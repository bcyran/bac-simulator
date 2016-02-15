#!/usr/bin/env python
from datetime import datetime, timedelta
from pprint import pprint
from math import exp


# Read alcohol intakes data from file
def read_data(data_file):
    # Read raw lines form file
    with open(data_file) as f:
        lines = f.readlines()

    # Split lines into separate cells
    lines.pop(0)
    raw_intakes = [i.split() for i in lines]

    # Create table containing time and amount of each intake
    intakes_tab = []
    for intake in raw_intakes:
        intake_time = datetime.strptime(intake[0], '%d.%m.%Y-%H:%M')
        intake_amount = float(intake[2]) / 100 * float(intake[1])
        intakes_tab.append([intake_time, intake_amount])

    return intakes_tab


# Read user preferences (first line of data file)
def read_prefs(data_file):
    with open(data_file) as f:
        raw_prefs = f.readline()

    raw_prefs = raw_prefs.split()

    user_prefs = {}
    user_prefs['sex'] = raw_prefs[0]
    user_prefs['weight'] = float(raw_prefs[1])
    user_prefs['height'] = float(raw_prefs[2])
    user_prefs['absorption_rate'] = float(raw_prefs[3])
    user_prefs['interval'] = float(raw_prefs[4])

    return user_prefs


# Calculate alcohol elimination rate (AER)
def calc_aer(sex, bac):
    if sex == 'female':
        aer = 0.17 + (bac * 0.05)
    elif sex == 'male':
        aer = 0.15 + (bac * 0.05)

    return aer


# Calculate volume distribution of alcohol (VDA) using Seidl method
def calc_vda(sex, weight, height):
    if sex == 'female':
        vda = 0.31 - 0.0064 * weight + 0.0045 * height

        # Crop values higher or lower than norm
        if vda < 0.44:
            vda = 0.44
        elif vda > 0.80:
            vda = 0.80

    elif sex == 'male':
        vda = 0.31 - 0.0048 * weight + 0.0046 * height

        if vda < 0.60:
            vda = 0.60
        elif vda > 0.87:
            vda = 0.87

    return vda


# Calculate amount of absorbed alcohol
def calc_absorbed(amount, absorption_rate, time):
    absorbed = amount * (1 - exp(-absorption_rate * time))

    # If absorbed amount is negative return 0
    if absorbed < 0:
        absorbed = 0

    return absorbed


# Calculate amount of eliminated alcohol during given time
def calc_eliminated(time, aer):
    eliminated = time * aer

    return eliminated


# Calculate blood alcohol concentration (BAC)
def calc_bac(absorbed, weight, vda, eliminated):
    bac = (absorbed / (weight * vda)) - eliminated

    return bac


# Create absorption table
# (alcohol absorbed for each intake at different timestamps)
def calc_abs_tab(intakes_tab, interval, absorption_rate):
    start_time = intakes_tab[0][0]
    intakes_count = len(intakes_tab)
    abs_tab = []

    current_time = start_time
    i = 0
    # Iterate until all intakes will be absorbed
    while True:
        # Add new row (timestamp)
        abs_tab.append([])

        # Iterate through columns (intakes)
        for j in range(0, intakes_count):
            # If this intake didn't yet happen ignore it
            if current_time < intakes_tab[j][0]:
                abs_tab[i].append(0)
                continue

            # Calculate and write absorbed amount
            amount = intakes_tab[j][1]
            delta = (current_time - intakes_tab[j][0]).seconds / 3600
            absorbed = calc_absorbed(amount, absorption_rate, delta)
            abs_tab[i].append(absorbed)

        # Stop loop when last intake is fully absorbed
        if (abs_tab[i][intakes_count - 1] == intakes_tab[intakes_count - 1][1] and
                intakes_tab[intakes_count - 1][0] < current_time):
            break

        # Add set interval to current time
        current_time = current_time + timedelta(minutes=interval)

        i += 1

    return abs_tab


# Table with total absorption, total elimination
# and current bac for each timestamp
def calc_bac_tab(abs_tab, interval, sex, weight, vda):
    bac_tab = []

    i = 0
    # Iterate until all alcohol is eliminated
    while True:
        # Sum absorption from current timestamp
        total_absorbed = 0
        if i < len(abs_tab):
            for intake_absorption in abs_tab[i]:
                total_absorbed += intake_absorption
        else:
            total_absorbed = bac_tab[i - 1][0]

        # Calculate total elimination
        if i > 0:
            prev_bac = bac_tab[i - 1][2]
            total_eliminated = bac_tab[i - 1][1]
            current_aer = calc_aer(sex, prev_bac)
            current_eliminated = current_aer * (interval / 60)
            total_eliminated += current_eliminated
        else:
            total_eliminated = 0

        # Calculate current BAC
        current_bac = calc_bac(total_absorbed, weight, vda, total_eliminated)

        if current_bac < 0.01:
            current_bac = 0

        # Write data to table
        bac_tab.append([total_absorbed, total_eliminated, current_bac])

        # Stop loop when BAC equals 0
        if bac_tab[i][2] == 0 and i != 0:
            break

        i += 1

    return bac_tab


# Print out calculated data
def print_data(bac_tab, start_time, interval):
    current_time = start_time
    print('TIME  - BAC')

    for i, row in enumerate(bac_tab):
        time = current_time.strftime('%H:%M')
        print('{0} - {1:.2f}'.format(time, row[2]))

        current_time = current_time + timedelta(minutes=interval)


# Main
def main():
    # Name of file containing all required data
    data_file = 'bac-simulator-data.txt'

    # Read data from file
    intakes_tab = read_data(data_file)
    user_prefs = read_prefs(data_file)

    # Calculate everything
    abs_tab = calc_abs_tab(
        intakes_tab,
        user_prefs['interval'],
        user_prefs['absorption_rate'])
    vda = calc_vda(
        user_prefs['sex'],
        user_prefs['weight'],
        user_prefs['height'])
    bac_tab = calc_bac_tab(
        abs_tab,
        user_prefs['interval'],
        user_prefs['sex'],
        user_prefs['weight'],
        vda)

    # And print result
    print_data(bac_tab, intakes_tab[0][0], user_prefs['interval'])


if __name__ == '__main__':
    main()
