from InputCreator import DSSATFile as DF
from InputCreator import DSSATModel as DM
from InputCreator import Fertilizer as Fert
from InputCreator import Irrigation as Irrigate
from DS_GREET import GREET
import os
import pandas as pd

'''
NITROGEN FERTILIZER SIMULATION
filei = 'cut'
'''
fert = [0,50,100,150,200,250,300]
for f in fert:
#     os.remove('saved.csv')
    Fert(mo =5,d=1,fmat='FE004',fapp='AP003',fdep=0,famn=f,famp=0,famk=0,famc=-99,famo=-99,focd=-99,fername=-99,nwyr='yes')
    gt = GREET(crop='Maize',cultivar='GDD2600',soil='Loam',weather='UNME',st_yr=2015,plant_month=5,plant_date=1,ppop=10.0,pmeth='S',row_space=75,pdepth=5,mode='B',irrsim='F',h_mo=10,h_day=15,w_suff='01',batchfile='run.v46',ofile='output.OUT',fuel='corn')
    g = gt.Model()
    path = 'C:\\DSSAT46\\DSSAT_wrapper\\src\\root\\nested\\SensA'
    os.rename('saved.csv',os.path.join(path,'WTP2_%d.csv'%(f)))
    file = open("Summary.OUT", 'r')
    r = file.readlines()[-1].split()
    file.close()
    y = int(r[20])