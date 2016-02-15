# BAC Simulator

Script simulating blood alcohol concentration (BAC) over time.

## About

BAC is estimated based on: sex, weight, height, time since drinking, presence of food in stomach, delay between drinking and absorption, and duration of drinking when it's important.

Used formulas:
* Modified Widmark formula - Posey & Mazayani (2007)
* Seidl formula for estimating the volume distribution of alcohol
* Relationship between alcohol elimination rate and increasing blood alcohol concentration ([link](http://www.ncbi.nlm.nih.gov/pubmed/17196778))

## Usage

To use BAC simulator you have to create file `bac-simulator-data.txt` in the same directory as script. File should be formatted like this:
```
sex weight height fill-level-of-stomach interval
dd.mm.rrrr-hh.mm alcohol-amount alcohol-% duration-of-drinking
...
```
* sex - male / female
* weight - Your weight in kilograms.
* height - Your height in centimeters.
* fill level of stomach - Expressed in number, typically from 2 to 7 (2 - full stomach, 7 - empty stomach).
* interval - Determines how big (in minutes) will be gap between estimations. For example if you are drinking at 12:00 and interval is set to 10, script will output BAC at 12:00, 12:10, 12:20, 12:30 and so on.
* alcohol amount - Amount of drank beverage (not pure alcohol) in milliliters.
* alcohol % - Alcohol percentage.
* duration of drinking - Optional but very useful when you are drinking over long period of time, e.g. sipping a beer. Like interval it should be specified in minutes.

Number of alcohol portions isn't limited

This is how data file would look for man who drank 50 ml of 40% liquor at 12:00 and 30 minutes later drank 5% beer in 20 minutes:
```
male 75 172 4 30
14.02.2016-12:00 50 40
14.02.2016-12:30 500 5 20
```
And output:
```
TIME  - BAC
12:00 - 0.00
12:30 - 0.24
13:00 - 0.52
13:30 - 0.55
14:00 - 0.47
14:30 - 0.39
15:00 - 0.31
15:30 - 0.22
16:00 - 0.14
16:30 - 0.06
17:00 - 0.00
```
