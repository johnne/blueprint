#!/usr/bin/env python

from argparse import ArgumentParser
import seaborn as sns
import csv,sys
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 8

## Define default ranges and order
ranges = {"Spring": {"Month": (4,4), "Day": (5,25), "Temperature": (3,5),"Chla": (4,14), "Phosphate": (0.1,0.5)},
          "Clear": {"Month": (4,6), "Day": (27,10), "Temperature": (5,15),"Chla": (0.5,2.0), "Phosphate": (0.2,0.4)},
          "Summer": {"Month": (6,8),"Day": (15,25), "Temperature": (10,20),"Chla": (0.2,4), "Phosphate": (0.1,0.35)},
          "Autumn": {"Month": (9,10),"Day": (10,25),"Temperature": (5,17),"Chla": (0.6,2.5), "Phosphate": (0.1,0.2)},
          "Winter": {"Month": (1,2), "Day": (11,25), "Temperature": (0.5,5),"Chla": (0.2,2), "Phosphate": (0.5,1.0)}
          }
order = ["Spring","Clear","Summer","Autumn","Winter"]
defvars = ["Date","Temperature","Chla","Phosphate"]
plotvars = ['Temperature', 'Salinity', 'Chla', 'Nitrate', 'Phosphate', 'Silicate', 'Ammonium', 'DOC', 'TotalN', 'NP', 'BacterialAbundance']

def match_ranges(ranges,meta,keys=["Date"]):
    meta["Period"] = ["Unknown"]*len(meta)
    date_counts = {}
    for period,d in ranges.iteritems():
        samples = []
        for key in keys:
            if key=="Date":
                start_d = dt.date(2012,d["Month"][0],d["Day"][0])
                end_d = dt.date(2012,d["Month"][1],d["Day"][1])
                start_dd = start_d.timetuple()
                end_dd = end_d.timetuple()
                start_J = start_dd.tm_yday
                end_J = end_dd.tm_yday
                samples+= list(meta[(meta.JulianDay>=start_J) & (meta.JulianDay<=end_J)].index)
            else:
                key_min = d[key][0]
                key_max = d[key][1]
                samples+=list(meta[(meta[key]>=key_min) & (meta[key]<=key_max)].index)
        for s in set(samples):
            if samples.count(s)==len(keys): 
                meta.loc[s,"Period"] = period
                try: date_counts[s]+=1
                except KeyError: date_counts[s] = 1
    for d,c in date_counts.iteritems():
        if c>1:
            meta.loc[d,"Period"] = "Unknown"
    return meta[meta["Period"].isin(ranges.keys())]

def addJulDay(meta):
    ## Calculate and add Julian Day column
    juldays = {}
    for item in meta.index:
        r = meta.loc[item,["Year","Month","Day"]]
        d = dt.date(int(r.Year),int(r.Month),int(r.Day))
        dd = d.timetuple()
        juldays[item] = dd.tm_yday
    x = pd.DataFrame([juldays]).T
    x.columns=["JulianDay"]
    metaJ = pd.concat([meta,x],axis=1)
    return metaJ

def main():
    parser = ArgumentParser()
    parser.add_argument("-m", "--metadata", type=str, required=True,
            help="Metadata table")
#    parser.add_argument("-v", "--vars", type=str,
#            help="Variables to use for definitions. Currently only includes combinations of 'Date','Chla',\
#            'Temperature','Phosphate'. Comma separated. Defaults to 'Chla,Temperature,Phosphate'")
    parser.add_argument("-r", "--rangedef", type=str, 
            help="Range definitions. Not implemented yet.")
    parser.add_argument("-p", "--plot", action="store_true",
            help="Produce boxplots of each period")
    args = parser.parse_args()

    ## Read metadata
    meta = pd.read_csv(args.metadata, header=0, index_col=0, sep="\t")
    meta.rename(columns=lambda x: x.rstrip(), inplace=True)

    ## Add Julian day column
    meta = addJulDay(meta)

    ## Match ranges
    meta_m = match_ranges(ranges,meta,keys=["Chla","Temperature","Phosphate"])
    
    ## Write definitions
    meta_m["Period"].to_csv(sys.stdout, sep="\t")

    if args.plot:
        for v in plotvars:
            sns.boxplot(data=meta_m,x="Period",y=v,order=order)
            plt.savefig(v+".pdf",bbox_inches="tight")
            plt.close()
    
if __name__ == '__main__':
    main()
