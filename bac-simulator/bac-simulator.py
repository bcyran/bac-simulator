#!/usr/bin/env python
# BAC Simulator | GPL v2.0 | https://github.com/sajran/bac-simulator

from datetime import datetime, timedelta
from pprint import pprint
from math import exp


# User preferences
USER_PREFS = {}


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

        # If time of drinking is given
        if len(intake) == 4:
            sub_intakes = split_intake(intake_time, intake_amount,
                                       int(intake[3]))
            intakes_tab.extend(sub_intakes)
            continue

        intakes_tab.append([intake_time, intake_amount])

    return intakes_tab


# Read user preferences (first line of data file)
def read_prefs(data_file):
    global USER_PREFS

    with open(data_file) as f:
        raw_prefs = f.readline()

    raw_prefs = raw_prefs.split()

    USER_PREFS['sex'] = raw_prefs[0]
    USER_PREFS['weight'] = float(raw_prefs[1])
    USER_PREFS['height'] = float(raw_prefs[2])
    USER_PREFS['abs_rate'] = float(raw_prefs[3])
    USER_PREFS['interval'] = float(raw_prefs[4])


# Split long drinking into smaller intakes
def split_intake(time, amount, duration):
    sub_amount = amount / duration
    sub_intakes = []

    # Proportional intake every minute
    current_time = time
    for i in range(0, duration):
        sub_intakes.append([current_time, sub_amount])
        current_time = current_time + timedelta(minutes=1)

    return sub_intakes


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
def calc_abs_tab(intakes_tab):
    start_time = intakes_tab[0][0]
    i_count = len(intakes_tab)
    abs_tab = []

    current_time = start_time
    i = 0
    # Iterate until all intakes will be absorbed
    while True:
        # Add new row (timestamp)
        abs_tab.append([])

        # Iterate through columns (intakes)
        for j in range(0, i_count):
            # If this intake didn't yet happen ignore it
            if current_time < intakes_tab[j][0]:
                abs_tab[i].append(0)
                continue

            # Calculate and write amount of alcohol absorbed so far
            amount = intakes_tab[j][1]
            delta = (current_time - intakes_tab[j][0]).seconds / 3600
            absorbed_so_far = calc_absorbed(amount, USER_PREFS['abs_rate'], delta)
            abs_tab[i].append(absorbed_so_far)

        # Stop loop when last intake is fully absorbed
        if (abs_tab[i][i_count - 1] == intakes_tab[i_count - 1][1] and
                intakes_tab[i_count - 1][0] < current_time):
            break

        # Add set interval to current time
        current_time = current_time + timedelta(minutes=USER_PREFS['interval'])

        i += 1

    return abs_tab


# Create table: timestamp | absorbed_so_far | eliminated_so_far | BAC
def calc_bac_tab(abs_tab, vda, first_intake, last_intake):
    bac_tab = []

    # Iterate until all alcohol is eliminated
    current_time = first_intake
    i = 0
    while True:
        # Sum absorption from current timestamp
        absorbed_so_far = 0
        if i < len(abs_tab):
            absorbed_so_far = sum(abs_tab[i])
        else:
            absorbed_so_far = bac_tab[i - 1][1]

        # Calculate amount of alcohol eliminated so far
        if i > 0:
            prev_bac = bac_tab[i - 1][3]
            eliminated_so_far = bac_tab[i - 1][2]
            current_aer = calc_aer(USER_PREFS['sex'], prev_bac)
            current_eliminated = current_aer * (USER_PREFS['interval'] / 60)
            eliminated_so_far += current_eliminated
        else:
            eliminated_so_far = 0

        # Calculate current BAC
        current_bac = calc_bac(absorbed_so_far, USER_PREFS['weight'],
                               vda, eliminated_so_far)

        if current_bac < 0.01:
            current_bac = 0

        # Write data to table
        bac_tab.append([current_time, absorbed_so_far, eliminated_so_far, current_bac])

        # Stop loop when BAC equals 0
        if current_bac == 0 and last_intake < current_time:
            break

        current_time = current_time + timedelta(minutes=USER_PREFS['interval'])
        i += 1

    return bac_tab


# Print out calculated data
def print_data(bac_tab):
    print('TIME  - BAC')

    for row in bac_tab:
        time = row[0].strftime('%H:%M')
        print('{0} - {1:.2f}'.format(time, row[3]))


# Main
def main():
    # Name of file containing all required data
    data_file = 'bac-simulator-data.txt'

    # Read user preferences
    read_prefs(data_file)

    # Read data from file
    intakes_tab = read_data(data_file)

    # Calculate everything
    vda = calc_vda(USER_PREFS['sex'], USER_PREFS['weight'],
                   USER_PREFS['height'])
    abs_tab = calc_abs_tab(intakes_tab)
    bac_tab = calc_bac_tab(abs_tab, vda, intakes_tab[0][0],
                           intakes_tab[len(intakes_tab) - 1][0])

    # And print result
    print_data(bac_tab)


if __name__ == '__main__':
    main()
