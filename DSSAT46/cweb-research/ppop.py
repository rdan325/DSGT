from InputCreator import DSSATFile as DF
from InputCreator import DSSATModel as DM
from InputCreator import Fertilizer as Fert
import xlwings as xw

pop = range(5,13)
fert = list(range(10,260,10))
fert = fert+[300,400,500,600]
print(fert)
wb = xw.Book('C:/DSSAT46/DSSAT_wrapper/src/root/nested/SensA/ppop.xlsx')
print('Next')
ws = xw.Sheet('Sheet1')
j = 66
i = 2
for p in pop:
    for f in fert:
        Fert(famn=f,fmat='FE004',fapp='AP003')
        a = DF(irrsim='F',weather='UNME',st_yr=2015,w_suff='01',ppop=p)
        a.Batch()
        a.Control()
        y,irr = DM().Run()
        print(i)
        print('%s%d'%(chr(j),i))
        ws.range('%s%d'%(chr(j),i)).value = y
        i += 1
    j+=1
    i=2
