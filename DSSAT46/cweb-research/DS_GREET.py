""""
Ryan Anderson
Wrapper used to connect DSSAT and GREET models using command line executables
Uses DSSAT_yield.py for DSSAT and CalculatorBatch.exe for GREET
"""

import os
import pandas as pd
import csv
import lxml.etree
from InputCreator import DSSATFile as DF
from InputCreator import DSSATModel as DM
from InputCreator import Irrigation as Irr
from InputCreator import Fertilizer as Fert
from InputCreator import Tillage as Till
from InputCreator import Chemicals as Chem
from PTW import E85, Gas
import xlwings as xw

class GREET(DF, DM):
    
    """
    Pathway ID names:
    Ethanol production from Corn          p51207813
    Ethanol produced in the US            p22939767
    Ethanol from stover (WTP)             p8711
    E85 Well-to-Wheels                    p52336395
    E10 Well-to-Wheels                    p57
    Dry Mill w/ Oil Extraction (process)  p79707210
    Dry Mill w/o Oil Extraction (process) p600
    Wet Mill (process)                    p601
    """
    
    def __init__(self,crop,cultivar,soil,weather,st_yr,plant_month,plant_date,ppop,pmeth,row_space,pdepth,irrsim,h_mo,h_day,w_suff,mode,batchfile,ofile,filei='New',fileo='out.greet',yr=2015,fuel='corn'):
        
        # water parameter is input in m^3 water per bu corn
        # N fertilizer parameter is input in kg/bu
        self.filei = filei
        self.fileo = fileo
        self.yr = yr
        self.fuel = fuel
        DF.__init__(self,crop,cultivar,soil,weather,st_yr,plant_month,plant_date,ppop,pmeth,row_space,pdepth,mode,irrsim,h_mo,h_day,w_suff)
        DM.__init__(self,mode,batchfile,ofile)
        
    def Model(self):
        
        DF.Batch(self)
        DF.Control(self)
        DM.Run(self)
        file = open('Summary.OUT')
        sm = file.readlines()[-1].split()
        i = float(sm[29])
        f = pd.read_csv('FertSched.csv')
        file = open("PlantGro.OUT", 'r')
        r = file.readlines()[-1].split()
        file.close()

        if self.fuel == 'corn':
            y = int(r[9])
            print('yield is',y)
            volume = (y*2.8/25.396) # GREET data; volume of ethanol in gal from kg of corn yield
            volume = volume/.85 # first value gives value of 100% pure ethanol; this gets total E85 fuel value in gallons
            energy = volume*87.493 # in MJ to calculate savings relative to using E0 gasoline
#             byproduct = 4.21*volume # dry DGS
#             wet_byproduct = 5.52*volume # Wet DGS
            if y > 0:
                water = i*10*25.396/y
            # conversion is total irr [mm/ha]*[1m/1000m]*[10^4 m^2/ha]*[25.369ha/yield bu]
                nfert = sum(f.ix[:,5])*25.366/y
                print(nfert)
                pfert = sum(f.ix[:,6])*25.366/y
                kfert = sum(f.ix[:,7])*25.366/y
            else:
                water = 0
                nfert = 0
                pfert = 0
                kfert = 0
            # rewrite .greet file as XML
            tree = lxml.etree.parse('%s.greet'%(self.filei))
            root = tree.getroot()
            # use E85 pathway for ethanol calculation
            ethanol = root.xpath("/greet/data/pathways/pathway[@id='52336395']/vertex[@id='f05e7f23-8896-4734-a440-ef834c96d156']/prefered_functional_unit")
            ethanol[0].attrib['amount'] = '%d'%(energy)
            # use E10 pathway for gasoline calculation
            gas = root.xpath("/greet/data/pathways/pathway[@id='57']/vertex[@id='972db13a-5d59-4186-ab74-0cf3a58894e2']/prefered_functional_unit")
            gas[0].attrib['amount'] = '%d'%(energy)
            ir = root.xpath("/greet/data/processes/stationary[@id='116']/input[@ref='88259336']/amount/year")
            ir[0].attrib['value'] = '%.4f;gal;0;gal;True;Publication Details&#xA;Title: Development of a Life Cycle Inventory of Water Consumption Associated with the Production of Transportation Fuels&#xA;Publication Date: October 2014&#xA;Authors: David Lampert , Hao Cai, Zhichao Wang, Jennifer Keisman , May Wu, Jeongwoo Han, Jennifer Dunn, Edward Frank, John Sullivan, Amgad Elgowainy, and Michael Wang&#xA;Link: https://greet.es.anl.gov/publication-water-lca&#xA;See Table 1: Summary of Water Consumption Factor Estimates;55944674107;Dieffenthaler, David ddieffenthaler@anl.gov;10/3/2014 10:56:06 AM;p_sproc-CornFarming-in-Water_Irrigation-0'%(water)
            nf = root.xpath("/greet/data/processes/stationary[@id='116']/input[@ref='104']/amount/year[@year='2014']")
            nf[0].attrib['value'] = '%.3f;g;0.70000000000000007;g;True;;f8f653ad-1e18-4e0f-8770-88403d10772c;Anderson, Ryan randerson49@huskers.unl.edu;8/29/2017 11:41:15 AM;p_sproc-CornFarming-in-Nitrogen-2014'%(nfert)
            pf = root.xpath("/greet/data/processes/stationary[@id='116']/input[@ref='96']/amount/year[@year='2014']")
            pf[0].attrib['value'] = '%.3f;g;0;g;True;;b7f5a42b-d88f-46ab-858d-80fc29c7e55e;Han, Jeongwoo jhan@anl.gov;9/30/2016 1:17:49 PM;p_sproc-CornFarming-in-PhosphoricacidP205-2014'%(pfert)
            kf = root.xpath("/greet/data/processes/stationary[@id='116']/input[@ref='97']/amount/year[@year='2014']")
            kf[0].attrib['value'] = '%.3f;g;0;g;True;;ddead291-d526-4f7b-ace6-e832e3074208;Han, Jeongwoo jhan@anl.gov;9/30/2016 1:19:06 PM;p_sproc-CornFarming-in-K2O-2014'%(kfert)
            tree.write('out.greet')

            # run GREET model
            os.system("GREETTest.exe %s %d p52336395" % (self.fileo, self.yr))
            os.system("GREETTest.exe %s %d p57" % (self.fileo, self.yr))

        
#         byproddf = pd.DataFrame([['Byproduct', byproduct],['Wet Byproduct',wet_byproduct],['Fuel amount',volume]], columns=['Parameters','Values'])
        # lbs DGS/gal ethanol
        file = open("Results-Pathway-52336395.txt",'r')
        e85 = file.readlines()
        file.close()
        file = open("Results-Pathway-57.txt",'r')
        e10 = file.readlines()
        file.close()
        e85 = [i.split('\t') for i in e85]
        e10 = [i.split('\t') for i in e10]

        with open('greetdata1.csv','w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, lineterminator = '\n')
            for l in e85:
                writer.writerow(l)
        csvfile.close()
        with open('greetdata2.csv','w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, lineterminator = '\n')
            for l in e10:
                writer.writerow(l)
        csvfile.close()
        low = pd.read_csv('greetdata1.csv')
        high = pd.read_csv('greetdata2.csv')
        print('water E85 is:',low.iloc[5])
        ghg_low = low.iloc[14][1]*23+low.iloc[15][1]*296+low.iloc[16][1]+low.iloc[17][1]
        ghg_high = high.iloc[14][1]*23+high.iloc[15][1]*296+high.iloc[16][1]+high.iloc[17][1]
        low.iloc[18] = ['GHG',ghg_low]
        high.iloc[18] = ['GHG',ghg_high]
        
        low.iloc[18] = ['GHG',ghg_low+E85(energy).ghg]
        high.iloc[18] = ['GHG',ghg_high+Gas(energy).ghg]
        print(E85(energy).ghg-Gas(energy).ghg)
        low.set_value(6,'2015\n',low.iloc[6][1]+E85(energy).voc)
        low.set_value(7,'2015\n',low.iloc[7][1]+E85(energy).co)
        low.set_value(8,'2015\n',low.iloc[8][1]+E85(energy).nox)
        high.set_value(6,'2015\n',high.iloc[6][1]+Gas(energy).voc)
        high.set_value(7,'2015\n',high.iloc[7][1]+Gas(energy).co)
        high.set_value(8,'2015\n',high.iloc[8][1]+Gas(energy).nox)
        length = pd.Series([0]*len(high['2015\n']))
        filler = {'Percent Footprint':length,'Abs Footprint':length}
        save = pd.DataFrame(filler)
        save['Percent Footprint'] = (low['2015\n'] - high['2015\n'])/high['2015\n']
        save['Abs Footprint'] = low['2015\n'] - high['2015\n']
        WTP = save['Abs Footprint'].iloc[18]
        print('WTP=',WTP)
        save = save.iloc[[1,4,5,6,7,8,9,11,18]]


#         low = low.append(pd.DataFrame(['GHG',ghg_low], columns = ['Items Per %d MJ'%(energy),'2015\n']),ignore_index=True)
#         high = high.append(pd.DataFrame(['GHG',ghg_high], columns = ['Items Per %d MJ'%(energy),'2015\n']),ignore_index=True)

        save.to_csv('saved.csv')

'''
FERTILIZER SCENARIO
fert = [0,50,100,150,200,250,300]
for f in fert:
#     os.remove('saved.csv')
    Fert(mo =5,d=1,fmat='FE004',fapp='AP003',fdep=0,famn=f,famp=0,famk=0,famc=-99,famo=-99,focd=-99,fername=-99,nwyr='yes')
    gt = GREET(crop='Maize',cultivar='GDD2600',soil='Loam',weather='UNME',st_yr=2015,plant_month=5,plant_date=1,ppop=10.0,pmeth='S',row_space=75,pdepth=5,mode='B',irrsim='F',h_mo=10,h_day=15,w_suff='01',batchfile='run.v46',ofile='output.OUT',fuel='corn')
    g = gt.Model()
    path = 'C:\\DSGT\\DSSAT46\\cweb-research\\SensA'
    os.rename('saved.csv',os.path.join(path,'WTP_%d.csv'%(f)))
    file = open("Summary.OUT", 'r')
    r = file.readlines()[-1].split()
    file.close()
    y = int(r[20])
#     print("PPOP",p,"FERTILIZER",f,"YIELD:",y)
#     i+=1
'''

'''
PPOP SCENARIO
pop = list(range(5,13))
fert = [90,110,110,120,120,120,120,130]

for i in range(0,8):
    Fert(mo =5,d=1,fmat='FE004',fapp='AP003',fdep=0,famn=fert[i],famp=0,famk=0,famc=-99,famo=-99,focd=-99,fername=-99,nwyr='yes')
    gt = GREET(crop='Maize',cultivar='GDD2600',soil='Loam',weather='UNME',st_yr=2015,plant_month=5,plant_date=1,ppop=pop[i],pmeth='S',row_space=75,pdepth=5,mode='B',irrsim='F',h_mo=10,h_day=15,w_suff='01',batchfile='run.v46',ofile='output.OUT',fuel='corn')
    g = gt.Model()
    path = 'C:/DSGT/DSSAT46/cweb-research/SensA'
    os.rename('saved.csv',os.path.join(path,'ppop_%d.csv'%(pop[i])))
'''

i = 77
j = 96
k = 115
pop = range(5,13)
fert = range(100,260,10)
wb = xw.Book('C:/DSSAT46/DSSAT_wrapper/src/root/nested/SensA/ppop_res.xlsx')
ws = xw.Sheet('ppop_5')
for p in pop:
    for f in fert:
        Fert(mo =5,d=1,fmat='FE004',fapp='AP003',fdep=0,famn=f,famp=0,famk=0,famc=-99,famo=-99,focd=-99,fername=-99,nwyr='yes')
        gt = GREET(crop='Maize',cultivar='GDD2600',soil='Loam',weather='UNME',st_yr=2015,plant_month=5,plant_date=1,ppop=p,pmeth='S',row_space=75,pdepth=5,mode='B',irrsim='F',h_mo=10,h_day=15,w_suff='01',batchfile='run.v46',ofile='output.OUT',fuel='corn')
        g = gt.Model()
        file = open("Summary.OUT", 'r')
        r = file.readlines()[-1].split()
        file.close()
        y = int(r[20])
        print(y)
        ws.range('%s%d'%(chr(i),k)).value = y
        fp = pd.read_csv('saved.csv')
        ghg = fp.loc[8,'Abs Footprint']
        print(ghg)
        ws.range('%s%d'%(chr(i),j)).value = ghg
        j+=1
        k+=1
    i+=1
    j=96
    k=115
        
'''
# OPTIMAL PLANT POPULATION SCENARIO ANALYSIS
import win32com.client
xl = win32com.client.Dispatch('Excel.Application')
xl.Visible = True
wb = xl.Workbooks.Add()
ws = wb.Worksheets.Add()
i = 66
pop = [6.0,7.0,8.0,9.0,10.0,11.0,12.0]
# pop = [5.0,6.0,7.0,8.0,9.0,10.0,11.0,12.0]
for p in pop:
    fert = [90,100,110,120,130,140,150,160,170,180]
    j = 2
    for f in fert:
        ws.Range('A%d'%(j)).value = f
        Fert(mo =5, d = 1, fmat = 'FE004', fapp = 'AP003', fdep = 10, famn = f, famp = 0, famk = 0, famc = -99, famo = -99, focd = -99, fername = -99, nwyr = 'yes')
        gt = GREET(crop='Maize', cultivar = 'medium', soil='Loam', weather='UNME', st_yr=2015, plant_month=5, plant_date=1, ppop=p, pmeth='S', row_space=75, pdepth=5, mode = 'B', irrsim='A', batchfile = 'run.v46', ofile = 'output.OUT', fuel = 'corn')
        gt.Model()
        save = pd.read_csv('saved.csv')
        ghg = save['Abs Footprint'].iloc[-1]
        ws.Range('%s%d'%(chr(i),j)).value = ghg
        j += 1
    i += 1
'''




'''
# IRRIGATION SCENARIO ANALYSIS
gt = GREET(crop='Maize', cultivar = 'medium', soil='Loam', weather='UNME', st_yr=2012, plant_month=5, plant_date=1, ppop=10.0, pmeth='S', row_space=75, pdepth=5, mode = 'B', irrsim='A', batchfile = 'run.v46', ofile = 'output.OUT', fuel = 'corn')
gt.Model()
os.rename('saved.csv','irr_dry_90.csv')
'''


'''
# SIMULATION FOR FERTILIZER SENSITIVITY ANALYSIS
fert = [0,50,100,150,200,250,300]
for f in fert:
    Fert(mo =5, d = 1, fmat = 'FE004', fapp = 'AP003', fdep = 10, famn = f, famp = 0, famk = 0, famc = -99, famo = -99, focd = -99, fername = -99, nwyr = 'yes')
    gt = GREET(crop='Maize', cultivar = 'medium', soil='Loam', weather='UNME', st_yr=2012, plant_month=5, plant_date=1, ppop=10.0, pmeth='S', row_space=75, pdepth=5, mode = 'B', irrsim='A', batchfile = 'run.v46', ofile = 'output.OUT', fuel = 'corn')
    gt.Model()
    os.rename('saved.csv','nfert_%d.csv'%(f))
    os.rename('saved.csv','WTP_dry_%d.csv'%(f))
'''



'''
SCENARIO ANALYSIS FOR OPTIMUM PLANT POPULATION
Fert(mo =5, d = 1, fmat = 'FE004', fapp = 'AP003', fdep = 10, famn = 250, famp = 0, famk = 0, famc = -99, famo = -99, focd = -99, fername = -99, nwyr = 'yes')
import win32com.client
xl = win32com.client.Dispatch('Excel.Application')
wb = xl.Workbooks.Add()
yrs = list(range(2001,2016))
pops = np.linspace(4,12,17)
for y in yrs:
    let = 'B'
    ws = wb.Worksheets.Add()
    ws.Range('A2').value = 'Fossil Fuel'
    ws.Range('A3').value = 'Petroleum'
    ws.Range('A4').value = 'VOC'
    ws.Range('A5').value = 'CO'
    ws.Range('A6').value = 'NOx'
    ws.Range('A7').value = 'PM10'
    ws.Range('A8').value = 'SOx'
    ws.Range('A9').value = 'GHG'
    ws.Range('A11').value = 'Prec'
    ws.Range('A12').value = 'Tmin'
    ws.Range('A13').value = 'Tmax'
    ws.Range('A14').value = 'Srad'
    for p in pops:
        gt = GREET(crop='Maize', cultivar = 'medium', soil='Loam', weather='UNME', st_yr=2015, plant_month=5, plant_date=1, ppop=10.0, pmeth='S', row_space=75, pdepth=5, mode = 'B', irrsim='A', batchfile = 'run.v46', ofile = 'output.OUT', fuel = 'corn')
        gt.Model()
        save = pd.read_csv('saved.csv')
        ws.Range('%s1'%(let)).value = p
        ws.Range('%s2'%(let)).value = save['Percent Savings'][0]
        ws.Range('%s3'%(let)).value = save['Percent Savings'][1]
        ws.Range('%s4'%(let)).value = save['Percent Savings'][2]
        ws.Range('%s5'%(let)).value = save['Percent Savings'][3]
        ws.Range('%s6'%(let)).value = save['Percent Savings'][4]
        ws.Range('%s7'%(let)).value = save['Percent Savings'][5]
        ws.Range('%s8'%(let)).value = save['Percent Savings'][6]
        ws.Range('%s9'%(let)).value = save['Percent Savings'][7]
        file = open('Summary.OUT')
        sm = file.readlines()[-1].split()
        ws.Range('B11').value = sm[78]
        ws.Range('B12').value = sm[74]
        ws.Range('B13').value = sm[73]
        ws.Range('B14').value = sm[75]
        let = chr(ord(let)+1)
        print(save)
        print(p)
        print(y)
wb.SaveAs('C:\\DSSAT46\\DSSAT_wrapper\\src\\root\\nested\\SensA\\ppop_scena_per.xlsx')
xl.Application.Quit()
'''
        

