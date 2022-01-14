# -*- coding: utf-8 -*-

import pandas as pd
import yfinance as yf
import time

"""
This function inputs a symbol (string) and outputs the options data for this stock
toCSV: if true, outputs the single option's data as a csv
bareMinimum: returns only name, date, strike price, bid, ask, call/put, last stock price
rawData: doesn't take out calls or puts that aren't in the money, doesn't remove mini options
timeIt: if true, returns how long executing this took
"""
def getOption(symbol, toCSV = False, timeIt = False, bareMinimum = False, rawData = False):
    start = time.time()
    #get the stock price
    sym = yf.Ticker(symbol)
    data = sym.history()
    price = (data.tail(1)['Close'].iloc[0]) #gets latest closing price

    #get the options chain for each expiration
    # Expiration dates
    exps = sym.options

    allOpt = pd.DataFrame()
    for e in exps:
        opt = sym.option_chain(e)
        
        #get your puts and calls: assign them 0 and 1
        calls = opt.calls
        calls['type'] = 0
        puts = opt.puts
        puts['type'] = 1
        
        #merge everything together and add on the expiration date
        opt = pd.DataFrame().append(calls).append(puts)
        opt['expirationDate'] = e
        allOpt = allOpt.append(opt, ignore_index=True)
        
    #check bare minimum:
    if(bareMinimum):
        dropThese = ['change', 'percentChange', 'volume', 'openInterest', 'impliedVolatility', 'inTheMoney', 'currency']
        allOpt.drop(dropThese, axis = 1, inplace = True) #reduces from 137 kb to 80 kb in case of apple
    if(not rawData):
        #remove any mini options (not regular), and bad puts and calls, etc.
        allOpt.drop(allOpt[(allOpt.type == 0) & (allOpt.strike <= price)].index, inplace = True)
        allOpt.drop(allOpt[(allOpt.type == 1) & (allOpt.strike >= price)].index, inplace = True)
        allOpt.drop(allOpt[allOpt.contractSize != "REGULAR"].index, inplace = True)

    #add price column
    allOpt['lastPrice'] = price

    #for testing purposes: export to CSV
    if(toCSV):
        allOpt.to_csv("oneOpt.csv")
    
    end = time.time()
    if(timeIt):
        print("The time of execution of above program is :", end-start) 
        
    #return the data
    return allOpt

"""
This function inputs list of stock symbols and outputs the options data for this stock
same arguments as single option.
toCSV: if true, outputs the TOTAL CHAINS' data into one dataframe and outputs as csv
bareMinimum: returns only name, date, strike price, bid, ask, call/put, last stock price
rawData: doesn't take out calls or puts that aren't in the money, doesn't remove mini options
timeIt: if true, returns how long executing this took
"""
def getListOptions(tickerList, toCSV = False, timeIt = False, bareMinimum = False, rawData = False):
    start = time.time()
    
    
    hasOpt = []
    noOpt = []

    #call getOption for each of them, merge
    try:
        optionsData = getOption(tickerList[0], timeIt, bareMinimum, rawData)
    except:
        print("no data for: ", tickerList[0])

    for i in range(1, len(tickerList)):
        try:
            thisDataFrame = getOption(tickerList[i], timeIt, bareMinimum, rawData)
            optionsData = optionsData.append(thisDataFrame, ignore_index = True)
            print("finished index", i, ":", tickerList[i])
            hasOpt.append(tickerList[i])
        except:
            print("no data for:", tickerList[i])
            noOpt.append(tickerList[i])
        
    #for testing purposes: export to CSV
    if(toCSV):
        optionsData.to_csv("allOpt.csv")
        try:
            pd.DataFrame(hasOpt).to_csv("hasOpt.csv")
            pd.DataFrame(noOpt).to_csv("noOpt.csv")
        except:
            print("Issue with list converstion")
    
    end = time.time()
    print("The time of execution of above program is :", ((end-start)), "seconds") 
    return optionsData

chain = getOption('AAPL') #averages between 6 and 8 seconds for a big stock
bunch = getListOptions(['AAPL', 'V', 'XON', 'FB'], toCSV = True)