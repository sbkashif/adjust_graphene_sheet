"""
adjust_coordinates.py
xx

Handles the primary functions
"""

import os
from adjust_graphene_sheet import functions
import sys
import numpy as np
import pandas as pd
import re

def adjust_coordinates(filename="graphene.gro", outfile="graphene_adjusted.gro"):
    install_dir=os.path.dirname(functions.__file__)
    print(install_dir)
    filename_withpath=os.path.join(install_dir,'data',filename)
    
    
    try:
        print("Opening file...\n ",filename_withpath)
        f=open(filename_withpath)

    except IOError as e:
        print("Unable to open" + filename +". Please check the file")
   
    coord=[]
    box=[] 
    n_atoms=0
    for idx,line in enumerate(f):
        if idx==1:
            n_atoms=int(line.split()[0])
        if idx>=2:
            parts=line.split()
            if len(parts)>3:
                coord.append([parts[0],parts[1],parts[2],float(parts[3]),float(parts[4]), float(parts[5])])
            elif len(parts)==3:
                box.append([parts[0],parts[1], parts[2]])
    labels=["resid","atom_type","index","x","y","z"]
    df=pd.DataFrame(coord,columns=labels)
    df.astype({'x': 'float64'}).dtypes
    df.astype({'y': 'float64'}).dtypes 
    df.astype({'z': 'float64'}).dtypes
    #pd.set_option('display.max_rows',df.shape[0]+1)

    min_y=df['y'].min()
    df['y']=df['y']-min_y
    min_x=df['x'].min()
    df['x']=df['x']-min_x
    min_x=df['x'].min()
    min_y=df['y'].min()
    print("Min_x,Min_y",min_x,min_y)
    max_x=df['x'].max()
    max_y=df['y'].max()
    print("Max_x,Max_y",max_x,max_y)
    
    print(df)
    
    #Calculating the shift for x
    order_y=df.sort_values(by=['y','x'])
    order_y['dx']=-order_y['x']+order_y['x'].shift(-1)
    ref_x=order_y.loc[order_y['y']==0,'dx']
    ref_x.drop(ref_x.tail(1).index,inplace=True)
    avg_x=ref_x.mean()
    shift_x=avg_x
    #print(ref_x,count_x)
    

    #Calculating the shift for y
    order_x=df.sort_values(by=['x','y'])
    order_x['dy']=-order_x['y']+order_x['y'].shift(-1)
    min_x=order_x['x'].min()
    ref_y=order_x.loc[order_x['x']==0,'dy']
    ref_y.drop(ref_y.tail(1).index,inplace=True)
    print(ref_y)
    avg_y=ref_y.iloc[1]
    count_y=ref_y.count()+1
    shift_y=avg_y
    
    print("Total shift needed",avg_x,avg_y)
    print("Per atom shift",shift_x,shift_y)
    
    #df.loc[(df['y'] != 0.0) & (df['x'] !=0.0), 'x']=df['x']-shift_x
    #df.loc[(df['x'] != 0.0) & (df['y'] !=0.0), 'y']=df['y']-shift_y
    
    df.loc[(df['x'] != 0.0), 'x']=df['x']-shift_x
    #df.loc[(df['y'] != 0.0), 'y']=df['y']-shift_y
    

    min_x=df['x'].min()
    min_y=df['y'].min()
    print(min_x,min_y)
    max_x=df['x'].max()
    max_y=df['y'].max()
    print(max_x,max_y)
    
    print(df)

    o=open(outfile,"w")
    o.write("Generated by adjust_graphene_sheet.py\n")
    o.write("   %d\n"%n_atoms)
    for ind,row in df.iterrows():
        resid_num=[int(s) for s in re.findall(r'-?\d+\.?\d*', row['resid'])][0]
        resid_str=''.join([i for i in row['resid'] if not i.isdigit()])
        o.write("%5d%-5s%5s%5d%8.3f%8.3f%8.3f\n"%(resid_num,resid_str,row['atom_type'],int(row['index']),row['x'],row['y'],row['z']))
    o.write("%s\t%s\t%s"%(box[0][0], box[0][1], box[0][2]))
    f.close()

   
if __name__ == "__main__":
    adjust_coordinates(filename,outfile)


