import os
import pandas as pd
import csv
import lxml.etree
from PTW import E85, Gas

# class gt(object):
        
def Model(yld,yr,irr,n,p,k,chem,mi,filei):
    
    volume = (yld*2.8/25.396) # GREET data; volume of ethanol in gal from kg of corn yield
    volume = volume/.85 # first value gives value of 100% pure ethanol; this gets total E85 fuel value in gallons
    energy = volume*87.493
    dgs = 4.21*volume
    
    if yld > 0:
        water = irr*10*25.396/yld
        # conversion is total irr [mm/ha]*[1m/1000m]*[10^4 m^2/ha]*[25.369ha/yield bu]
        nfert = n*25.366/yld
        pfert = p*25.366/yld
        kfert = k*25.366/yld
    else:
        water = 0
        nfert = 0
        pfert = 0
        kfert = 0
    
    tree = lxml.etree.parse('%s.greet'%(filei))
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
    dist = root.xpath("/greet/data/processes/transportation[@id='54314482']/step/distance/year")
    dist[0].attrib['value'] ='48280.32;mi;%f;mi;False;;54314483;Anderson, Ryan randerson49@huskers.unl.edu;2/14/2018 5:12:43 PM;p_tproc-EtOHRemulatedGasoline(E85)AsaTranspFueldistributionstep-HeavyHeavyDutyTruck0-dist-0'%(mi*1609.34) # need to convert from miles to meters
    tree.write('out.greet')

    # run GREET model
    os.system("GREETTest.exe %s %d p52336395" % ('out.greet', yr))
    os.system("GREETTest.exe %s %d p57" % ('out.greet', yr))
    
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
    
    ghg_low = low.iloc[14][1]*23+low.iloc[15][1]*296+low.iloc[16][1]+low.iloc[17][1]
    ghg_high = high.iloc[14][1]*23+high.iloc[15][1]*296+high.iloc[16][1]+high.iloc[17][1]
    low.iloc[18] = ['GHG',ghg_low]
    high.iloc[18] = ['GHG',ghg_high]
    
    low.iloc[18] = ['GHG',ghg_low+E85(energy).ghg]
    high.iloc[18] = ['GHG',ghg_high+Gas(energy).ghg]
    size = high.shape[0]
    length = pd.Series([0]*size)
    filler = {'Abs Footprint':length}
    save = pd.DataFrame(filler)
    save['Abs Footprint'] = low['%d\n'%(yr)] - high['%d\n'%(yr)]
#     save['Abs Footprint'] = low['2015\n'] - high['2015\n']
    save = save.iloc[[1,4,5,18]]
    save = save.rename(index={1:'Fossil Fuel Footprint',4:'Petroleum Footprint',5:'Water Footprint',18:'GHG Footprint'})
    dict = save.to_dict('dict')

    return dict['Abs Footprint'], dgs
        
def corn(yld,yr,irr,n,p,k,chem,mi,filei):
    
    if yld > 0:
        water = irr*10*25.396/yld
        # conversion is total irr [mm/ha]*[1m/1000m]*[10^4 m^2/ha]*[25.369ha/yield bu]
        nfert = n*25.366/yld
        pfert = p*25.366/yld
        kfert = k*25.366/yld
    else:
        water = 0
        nfert = 0
        pfert = 0
        kfert = 0
    tree = lxml.etree.parse('%s.greet'%(filei))
    root = tree.getroot()
    
    corn = root.xpath("/greet/data/pathways/pathway[@id='2016']/vertex[@id='000007e0-0001-0000-efec-e00000000000']/prefered_functional_unit")
    corn[0].attrib['amount'] = '%d'%(yld)
    ir = root.xpath("/greet/data/processes/stationary[@id='116']/input[@ref='88259336']/amount/year")
    ir[0].attrib['value'] = '%.4f;gal;0;gal;True;Publication Details&#xA;Title: Development of a Life Cycle Inventory of Water Consumption Associated with the Production of Transportation Fuels&#xA;Publication Date: October 2014&#xA;Authors: David Lampert , Hao Cai, Zhichao Wang, Jennifer Keisman , May Wu, Jeongwoo Han, Jennifer Dunn, Edward Frank, John Sullivan, Amgad Elgowainy, and Michael Wang&#xA;Link: https://greet.es.anl.gov/publication-water-lca&#xA;See Table 1: Summary of Water Consumption Factor Estimates;55944674107;Dieffenthaler, David ddieffenthaler@anl.gov;10/3/2014 10:56:06 AM;p_sproc-CornFarming-in-Water_Irrigation-0'%(water)
    nf = root.xpath("/greet/data/processes/stationary[@id='116']/input[@ref='104']/amount/year[@year='2014']")
    nf[0].attrib['value'] = '%.3f;g;0.70000000000000007;g;True;;f8f653ad-1e18-4e0f-8770-88403d10772c;Anderson, Ryan randerson49@huskers.unl.edu;8/29/2017 11:41:15 AM;p_sproc-CornFarming-in-Nitrogen-2014'%(nfert)
    pf = root.xpath("/greet/data/processes/stationary[@id='116']/input[@ref='96']/amount/year[@year='2014']")
    pf[0].attrib['value'] = '%.3f;g;0;g;True;;b7f5a42b-d88f-46ab-858d-80fc29c7e55e;Han, Jeongwoo jhan@anl.gov;9/30/2016 1:17:49 PM;p_sproc-CornFarming-in-PhosphoricacidP205-2014'%(pfert)
    kf = root.xpath("/greet/data/processes/stationary[@id='116']/input[@ref='97']/amount/year[@year='2014']")
    kf[0].attrib['value'] = '%.3f;g;0;g;True;;ddead291-d526-4f7b-ace6-e832e3074208;Han, Jeongwoo jhan@anl.gov;9/30/2016 1:19:06 PM;p_sproc-CornFarming-in-K2O-2014'%(kfert)
    dist = root.xpath("/greet/data/processes/transportation[@id='40000']/step[@dest_ref='41']/distance/year")
    dist[0].attrib['value'] ='64373.76;mi;%f;mi;False;;tp_40000_st20_step_10410_dist;Dieffenthaler, David ddieffenthaler@anl.gov;11/27/2013 2:43:01 PM;p_tproc-CornTranspfromField2BiofuelRefinerystep-HeavyHeavyDutyTruck0-dist-0'%(mi*1609.34) # need to convert from miles to meters
    tree.write('out.greet')

    os.system("GREETTest.exe %s %d p2016" % ('out.greet', yr))
    file = open("Results-Pathway-2016.txt",'r')
    fp = file.readlines()
    file.close()
    fp = [i.split('\t') for i in fp]
    with open('greetdata.csv','w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, lineterminator = '\n')
        for l in fp:
            writer.writerow(l)
    low = pd.read_csv('greetdata.csv',index_col=0)
    low.loc['GHG-100 (g)'] = low.loc['CO2 (g)']+low.loc['CO2_Biogenic (g)']+low.loc['CH4 (g)']*23+low.loc['N2O (g)']*296
    return low
    
def eth(yld,yr,irr,n,p,k,chem,mi,filei):
    
    volume = (yld*2.8/25.396) # GREET data; volume of ethanol in gal from kg of corn yield
    volume = volume/.85 # first value gives value of 100% pure ethanol; this gets total E85 fuel value in gallons
    energy = volume*87.493
    dgs = 4.21*volume
    
    if yld > 0:
        water = irr*10*25.396/yld
        # conversion is total irr [mm/ha]*[1m/1000m]*[10^4 m^2/ha]*[25.369ha/yield bu]
        nfert = n*25.366/yld
        pfert = p*25.366/yld
        kfert = k*25.366/yld
    else:
        water = 0
        nfert = 0
        pfert = 0
        kfert = 0
    
    tree = lxml.etree.parse('%s.greet'%(filei))
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
    dist = root.xpath("/greet/data/processes/transportation[@id='54314482']/step/distance/year")
    dist[0].attrib['value'] ='48280.32;mi;%f;mi;False;;54314483;Anderson, Ryan randerson49@huskers.unl.edu;2/14/2018 5:12:43 PM;p_tproc-EtOHRemulatedGasoline(E85)AsaTranspFueldistributionstep-HeavyHeavyDutyTruck0-dist-0'%(mi*1609.34) # need to convert from miles to meters
    tree.write('out.greet')

    os.system("GREETTest.exe %s %d p52336395" % ('out.greet', yr))
    file = open("Results-Pathway-52336395.txt",'r')
    fp = file.readlines()
    file.close()
    fp = [i.split('\t') for i in fp]
    with open('greetdata.csv','w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, lineterminator = '\n')
        for l in fp:
            writer.writerow(l)
    low = pd.read_csv('greetdata.csv',index_col=0)
    low.loc['GHG-100 (g)'] = low.loc['CO2 (g)']+low.loc['CO2_Biogenic (g)']+low.loc['CH4 (g)']*23+low.loc['N2O (g)']*296
    return low, dgs
    
