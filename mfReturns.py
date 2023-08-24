import sys
import json
from mftool import Mftool

mf = Mftool()

def getAnnualizedReturns(absolute_ret, years):
    return (pow((1.0*absolute_ret) / 100 + 1, 1.0/years) - 1)*100

def rollingReturns():                                                                                                                                                                      
    scheme_codes = sys.argv[2].split(",")                                                                                                                                                  
    years = sys.argv[3]                                                                                                                                                                    
                                                                                                                                                                                           
    for scheme_code in scheme_codes:                                                                                                                                                       
        data = json.loads(mf.get_scheme_historical_nav(scheme_code, as_json=True))                                                                                                         
        print(data['scheme_name'])                                                                                                                                                         
        data = data['data']                                                                                                                                                                
                                                                                                                                                                                           
        for year in years.split(","):                                                                                                                                                      
            year = int(year)                                                                                                                                                               
            returns = []                                                                                                                                                                   
            for i in range(len(data)-year*247-1):                                                                                                                                          
                initial_nav = float(data[i+year*247]['nav'])                                                                                                                               
                final_nav = float(data[i]['nav'])                                                                                                                                          
                try:                                                                                                                                                                       
                    returns.append(getAnnualizedReturns((final_nav - initial_nav)*100 / initial_nav, year))                                                                                
                except:                                                                                                                                                                    
                    continue                                                                                                                                                               
            if len(returns) == 0:                                                                                                                                                          
                print("0 / 0 / 0")                                                                                                                                                         
                continue                                                                                                                                                                   
                                                                                                                                                                                           
            max_ret = str(round(max(returns),2))                                                                                                                                           
            min_ret = str(round(min(returns),2))                                                                                                                                           
            avg_ret = str(round(sum(returns)/len(returns),2))                                                                                                                              
            print(min_ret + " / " + avg_ret + " / " + max_ret) 

def p2pReturns():
    scheme_code = sys.argv[2]
    initial_date = sys.argv[3]
    final_date = sys.argv[4]
    initial_nav = 0
    final_nav = 0

    data = json.loads(mf.get_scheme_historical_nav(scheme_code, as_json=True))
    print(data['scheme_name'])

    for i in data['data']:
        if i['date'] == initial_date:
            initial_nav = float(i['nav'])
        if i['date'] == final_date:
            final_nav = float(i['nav'])
    print(float((final_nav - initial_nav)*100 / initial_nav))

def calReturns():
    scheme_codes = sys.argv[2].split(",")
    years = sys.argv[3].split(",")

    for scheme_code in scheme_codes:
        data = json.loads(mf.get_scheme_historical_nav(scheme_code, as_json=True))
        print(data['scheme_name'])
        returns = []

        for year in years:
            initial_nav = 0
            final_nav = 0
            for i in data['data']:
                if i['date'] == "01-01-"+year or\
                        i['date'] == "02-01-"+year or\
                        i['date'] == "03-01-"+year or\
                        i['date'] == "04-01-"+year:
                            initial_nav = float(i['nav'])
                if i['date'] == "31-12-"+str(int(year)) or\
                        i['date'] == "01-01-"+str(int(year)+1) or\
                        i['date'] == "02-01-"+str(int(year)+1) or\
                        i['date'] == "03-01-"+str(int(year)+1):
                            final_nav = float(i['nav'])
            if initial_nav == 0 or final_nav == 0:
                returns.append("0.0")
            else:
                returns.append(str(round((final_nav - initial_nav)*100 / initial_nav, 2)))
        print(' / '.join(returns))

def main():
    function = sys.argv[1]
    if (function == "p2p"):
        p2pReturns()
    if (function == "cal"):
        calReturns()
    if (function == "rolling"):
        rollingReturns()

main()
