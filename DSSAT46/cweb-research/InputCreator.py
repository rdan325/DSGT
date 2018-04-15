'''
Created on Jun 16, 2017

@author: microwave
'''
import os
import csv
import sys
import numpy as np
import pandas as pd
import datetime as dt
from numpy import mean
class DSSATFile(object):


# IrrSched.csv should be a dataframe containing: 1, date, method, amount for each scheduled irrigation

        def __init__(self, crop='Maize', cultivar = 'GDD2600', soil='Loam', weather='UNME', st_yr=2015, plant_month=5, plant_date=1, ppop=10.0, pmeth='S', row_space=75, pdepth=5, mode='B', irrsim = 'F', h_mo=10, h_day=15,w_suff='01'):
                # initialization
                self.crop = crop
                self.cultivar = cultivar
                self.soil = soil
                self.weather = weather
                self.st_yr = st_yr
                self.plant_month = plant_month
                self.plant_date = plant_date
                self.ppop = ppop
                self.pmeth = pmeth
                self.row_space = row_space
                self.pdepth = pdepth
                self.mode = mode
                self.irrsim = irrsim
                self.h_mo = h_mo
                self.h_day = h_day
                self.w_suff = w_suff
                self.irr = "IrrSched.csv"
                self.fert = "FertSched.csv"
                self.org = "OrgSched.csv"
                self.till = "TillSched.csv"
                self.chem = "ChemSched.csv"
        
        def Batch(self):

                """
                    This function is used to write the batch file.
                    All modes except for batch mode were taken out as this mode is only
                    used for individual treatments
                """

                batchfile = open("run.v46", "w")
# Change .BTX file to .MZX, .SBX, or .WHX
                if self.crop == "Maize":
                    batchfile.write("$BATCH(BATCH)\n!\n")
                    batchfile.write(
                            "@FILEX                                                                                        TRTNO     RP     SQ     OP     CO\n")
                    batchfile.write(
                            "%s%s.MZX                                                                                     %d       %d      %d      %d      %d" % (
                                    self.weather, str(self.st_yr), 1, 1, 0, 0, 0))
                elif self.crop == "Soybean":
                    batchfile.write("$BATCH(BATCH)\n!\n")
                    batchfile.write(
                            "@FILEX                                                                                        TRTNO     RP     SQ     OP     CO\n")
                    batchfile.write(
                            "%s%s.SBX                                                                                     %d       %d      %d      %d      %d" % (
                                    self.weather, str(self.st_yr), 1, 1, 0, 0, 0))
                elif self.crop == "Wheat":
                    batchfile.write("$BATCH(BATCH)\n!\n")
                    batchfile.write(
                            "@FILEX                                                                                        TRTNO     RP     SQ     OP     CO\n")
                    batchfile.write(
                            "%s%s.WHX                                                                                     %d       %d      %d      %d      %d" % (
                                    self.weather, str(self.st_yr), 1, 1, 0, 0, 0))
# Removed debug mode option
                batchfile.close()
                return

        def Control(self):

                """
                   This function is used to write the experiment file.
                   Returns: Input experiment file. e.g., DTCM1951.GSX
                """

                if self.mode == "S":
                        file = open("%s%s.GSX" % (self.weather, str(self.st_yr)), "w")
                elif self.mode == "N":
                        file = open("%s%s.SNX" % (self.weather, str(self.st_yr)), "w")
                elif self.mode == "Q":
                        file = open("%s%s.SQX" % (self.weather, str(self.st_yr)), "w")
                elif self.mode == "B":
                    if self.crop == "Maize":
                        file = open("%s%s.MZX" % (self.weather, str(self.st_yr)), "w")
                    if self.crop == "Soybean":
                        file = open("%s%s.SBX" % (self.weather, str(self.st_yr)), "w")
                    if self.crop == "Wheat":
                        file = open("%s%s.WHX" % (self.weather, str(self.st_yr)), "w")
# Removed debug mode                        
                else:
                        print("Missing Running Mode!\n")
                        exit()
                file.write("*EXP.DETAILS: %s%s\n" % (self.weather, str(self.st_yr)))
                file.write("\n*GENERAL\n@PEOPLE\n-99\n@ADDRESS\n-99\n@SITE\n-99\n")
#                 file.write("    %d   %d   %d   %d   %d   %d   %d   %d   %d   %d\n" % (
#                         -99, -99, -99, -99, -99, -99, -99, -99, -99, -99))
                # Treatment
                file.write("\n*TREATMENTS                        -------------FACTOR LEVELS------------\n")
                file.write("@N R O C TNAME.................... CU FL SA IC MP MI MF MR MC MT ME MH SM\n")
                #file.write("%2d %d %d %d %s                    %d  %d  %d  %d  %d  %d  %d  %d  %d  %d  %d  %d  %d\n" % (1, 1, 0, 0, "SPATIAL", 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1))
                file.write("%2d %d %d %d %-25s%3s%3s%3s%3s%3s%3s%3s%3s%3s%3s%3s%3s%3s\n" % (1, 1, 1, 0, "Sim", 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1))
                # Cultivar
                file.write("\n*CULTIVARS\n")
                file.write("@C CR INGENO CNAME\n")
                if self.crop == "Maize":
                    if self.cultivar == 'short':
                        file.write("%2s %s %s %s\n" % (1, "MZ", "990003", "SHORT SEASON"))
                    elif self.cultivar == 'medium':
                        file.write("%2s %s %s %s\n" % (1, "MZ", "990002", "MEDIUM SEASON"))
                    elif self.cultivar == 'long':
                        file.write("%2s %s %s %s\n" % (1, "MZ", "990001", "LONG SEASON"))
                    elif self.cultivar == 'pioneer':
                        file.write("%2s %s %s %s %d\n" % (1, "MZ", "IB0012", "PIO", 3382))
                    elif self.cultivar == 'GDD2700':
                        file.write("%2s %s %s %s\n" % (1, "MZ", "PC0004", "2700-2750 GDD"))
                    elif self.cultivar == 'GDD2650':
                        file.write("%2s %s %s %s\n" % (1, "MZ", "PC0003", "2650-2700 GDD"))
                    elif self.cultivar == 'GDD2600':
                        file.write("%2s %s %s %s\n" % (1, "MZ", "PC0002", "2600-2650 GDD"))
                    elif self.cultivar == 'GDD2500':
                        file.write("%2s %s %s %s\n" % (1, "MZ", "PC0001", "2500-2600 GDD"))
                elif self.crop == "Wheat":
                        file.write("%2s %s %s %s\n" % (1, "WH", "IB0488", "NEWTON"))
                elif self.crop == "Soybean":
                        file.write("%2s %s %s %s\n" % (1, "SB", "IB0011", "EVANS"))
                else:
                        print("ERROR cultivar\n")
                        exit()
                # Fields for weather
                yr = str(self.st_yr)[2:]
                yr = yr + self.w_suff
                file.write("\n*FIELDS\n")
                file.write("@L ID_FIELD WSTA....  FLSA  FLOB  FLDT  FLDD  FLDS  FLST SLTX  SLDP  ID_SOIL    FLNAME\n")
                #if self.weather == "DTCM":
                if self.soil == "Clay":
                    file.write("%2s %s%4s %s%s   %d   %d   %s   %d   %d   %s  %d   %d  %s %d\n" % (
                        1, self.weather, "0001", self.weather, yr, -99, -99, -99, -99, -99, -99, -99, -99, "IB00000001", -99))
                elif self.soil == "Loam":
                    file.write("%2s %s%4s %s%s   %d   %d   %s   %d   %d   %s  %d   %d  %s %d\n" % (
                        1, self.weather, "0001", self.weather, yr, -99, -99, -99, -99, -99, -99, -99, -99, "IB00000005", -99))
#                         1, self.weather, "0001", self.weather, yr, -99, -99, -99, -99, -99, -99, -99, -99, "IB00000005", -99))
                elif self.soil == "Sand":
                    file.write("%2s %s%4s %s%s   %d   %d   %s   %d   %d   %s  %d   %d  %s %d\n" % (
                        1, self.weather, "0001", self.weather, yr, -99, -99, -99, -99, -99, -99, -99, -99, "IB00000007", -99))
                else:
                    print("ERROR soil\n")
                    exit()
#===============================================================================
#                 #else:
# 
#                         print("ERROR field\n")
# 
#                         exit()
#===============================================================================
# Original only uses DTCM, must allow for multiple weather files. Still only uses .CLI files

                file.write("@L ...........XCRD ...........YCRD .....ELEV .............AREA .SLEN .FLWR .SLAS FLHST FHDUR\n")
                file.write("%2s             %d             %d       %d               %d   %d   %d   %d   %d   %d\n" % (1, -99, -99, -99, -99, -99, -99, -99, -99, -99))
                file.write("\n*INITIAL CONDITIONS\n")
                file.write("@C   PCR ICDAT  ICRT  ICND  ICRN  ICRE  ICWD ICRES ICREN ICREP ICRIP ICRID ICNAME\n")
                date = dt.datetime(self.st_yr, 3, 1)
# Start simulation on March 1st 
                doy = date.strftime("%y%j")
                file.write("%2s    %2s %5s   %d   %d     %d     %d   %d   %d   %d   %d   %d   %d %d\n" % (
                        1, "MZ", doy, 200, -99, 1, 1, -99, -99, -99, -99, -99, -99, -99))
# Soil layer parameters
                file.write("@C  ICBL  SH2O  SNH4  SNO3\n")
                file.write("%2s  %3s  %.2f  %.1f  %.1f\n" % (1, 10, 0.21, 0.1, 0.9))
                file.write("%2s  %3s  %.2f  %.1f  %.1f\n" % (1, 20, 0.21, 0.1, 0.9))
                file.write("%2s  %3s  %.2f  %.1f  %.1f\n" % (1, 41, 0.24, 0.1, 0.9))
                file.write("%2s  %3s  %.2f  %.1f  %.1f\n" % (1, 71, 0.31, 0.1, 0.9))
                file.write("%2s  %3s  %.2f  %.1f  %.1f\n" % (1, 101, 0.32, 0.1, 0.9))
                file.write("%2s  %3s  %.2f  %.1f  %.1f\n" % (1, 126, 0.28, 0.1, 0.9))
                file.write("%2s  %3s  %.2f  %.1f  %.1f\n" % (1, 151, 0.28, 0.1, 0.9))
                # planting details
                file.write("\n*PLANTING DETAILS\n")
                file.write(
                        "@P PDATE EDATE  PPOP  PPOE  PLME  PLDS  PLRS  PLRD  PLDP  PLWT  PAGE  PENV  PLPH  SPRL                        PLNAME\n")
                pdate = dt.datetime(self.st_yr, self.plant_month, self.plant_date)
                pdoy = pdate.strftime("%y%j")
#                 if len(str(self.ppop)) == 3:
                file.write(
                    "%2s %5s  %d %6.1f %6.1f    %s     %s    %d    %d    %d    %d   %d   %d   %d   %d                      %d\n" % (
                        1, pdoy, -99, self.ppop, self.ppop, self.pmeth, "R", self.row_space, 0, self.pdepth, -99, -99, -99, -99, -99, -99))
#                 elif len(str(self.ppop)) == 4:
#                     file.write(
#                         "%2s %5s  %d   %.1f   %.1f    %s     %s    %d    %d    %d    %d   %d   %d   %d   %d                      %d\n" % (
#                             1, pdoy, -99, self.ppop, self.ppop, self.pmeth, "R", self.row_space, 0, self.pdepth, -99, -99, -99, -99, -99, -99))
                # irrigation
                # doy(a,b) takes YEAR from IC and MONTH and DAY from MgtData and puts them into DSSAT compatible date
                def doy(a,b):
                    return dt.datetime(self.st_yr,a,b).strftime("%y%j")
                
                file.write("\n*IRRIGATION AND WATER MANAGEMENT\n")
                file.write("@I  EFIR  IDEP  ITHR  IEPT  IOFF  IAME  IAMT IRNAME\n")
                file.write(
                        "%2s    %2s    %d    %d   %d %s %s    %d %d\n" % (1, 1, 30, 50, 100, "GS000", "IR004", 10, -99))
                file.write("@I IDATE  IROP IRVAL\n")
                i = pd.read_csv(self.irr)
                i['DATE'] = i.apply(lambda row: doy(row['MONTH'],row['DAY']),axis=1)
                for idate in i.index:
                    file.write(
                        "%2s %5s %5s    %d\n" % (1, i['DATE'][idate], i['ROP'][idate], i['VAL'][idate]))
                    
                # fertilizers
                file.write("\n*FERTILIZERS (INORGANIC)\n")
                file.write("@F FDATE  FMCD  FACD  FDEP  FAMN  FAMP  FAMK  FAMC  FAMO  FOCD FERNAME\n")
                f = pd.read_csv(self.fert)
                f['DATE'] = f.apply(lambda row: doy(row['MONTH'],row['DAY']),axis=1)
                for fdate in f.index:
                    file.write(
                        "%2s %5s %5s %5s %5d %5d %5d %5d %5d %5d %5d %3d\n" % (1, f['DATE'][fdate], f['FMCD'][fdate], f['FACD'][fdate], f['FDEP'][fdate], f['FAMN'][fdate], f['FAMP'][fdate], f['FAMK'][fdate], f['FAMC'][fdate], f['FAMO'][fdate], f['FOCD'][fdate], f['FERNAME'][fdate]))
                
                # Organic Ammendments
                file.write("\n*RESIDUES AND ORGANIC FERTILIZER\n")
                file.write("@R RDATE  RCOD  RAMT  RESN  RESP  RESK  RINP  RDEP  RMET RENAME\n")
                r = pd.read_csv(self.org)
                r['DATE'] = r.apply(lambda row: doy(row['MONTH'],row['DAY']),axis=1)
                for rdate in r.index:
                    file.write(
                        "%2s %5s %5s %5d %5d %5d %5d %5d %5d %5s %3d\n"%(1,r['DATE'][rdate],r['RCOD'][rdate],r['RAMT'][rdate],r['RESN'][rdate],r['RESP'][rdate],r['RESK'][rdate],-99,-99,r['RMET'][rdate],-99))
                    
                # Chemical Applications
                file.write("\n*CHEMICAL APPLICATIONS\n")
                file.write("@C CDATE CHCOD CHAMT  CHME CHDEP   CHT..CHNAME\n")
                c = pd.read_csv(self.chem)
                c['DATE'] = c.apply(lambda row: doy(row['MONTH'],row['DAY']),axis=1)
                for cdate in c.index:
                    file.write(
                        "%2s %5s %5s    %d %5s %d   %d  %d\n" % (1, c['DATE'][cdate], c['CHCOD'][cdate], c['CHAMT'][cdate], c['CHME'][cdate], c['CHDEP'][cdate], c['CHT'][cdate], c['CHNAME'][cdate]))
                    
                # Tillage
                file.write("\n*TILLAGE AND ROTATIONS\n")
                file.write("@T TDATE TIMPL  TDEP TNAME\n")
                t = pd.read_csv(self.till)
                t['DATE'] = t.apply(lambda row: doy(row['MONTH'],row['DAY']),axis=1)
                file.write("%2s %5s %5s    %d  %d\n" % (1, t['DATE'][0],t['TIMPL'][0],t['TDEP'][0],t['TNAME'][0]))
                
                # Harvest
                file.write("\n*HARVEST DETAILS\n")
                file.write("@H HDATE  HSTG  HCOM HSIZE   HPC  HBPC HNAME\n")
                hdoy = doy(self.h_mo,self.h_day)
                file.write("%2s %5s %5s     %s   %s   %s   %s %s\n" % (1, hdoy,"GS000","H",-99,-99,-99,self.crop))
                
                #Simulation controls

                file.write("\n*SIMULATION CONTROLS\n")
                file.write("@N GENERAL     NYERS NREPS START SDATE RSEED SNAME.................... SMODEL\n")
                sdoy = int(pdoy)-30 # Start simulation 30 days before planting date
                file.write("%2s %2s             %2s     %d     %s %5s  %d %s\n" % (1, "GE", 1, 1, "S", sdoy, 2150, "DEFAULT"))
                file.write("@N OPTIONS     WATER NITRO SYMBI PHOSP POTAS DISES  CHEM  TILL   CO2\n")
                file.write("%2s %2s              %s     %s     %s     %s     %s     %s     %s     %s     %s\n" % (1, "OP", "Y", "Y", "N", "N", "N", "N", "N", "Y", "D"))
# Does not yet simulate P or K
# Symbiosis not simulated
                file.write("@N METHODS     WTHER INCON LIGHT EVAPO INFIL PHOTO HYDRO NSWIT MESOM MESEV MESOL\n")
                file.write("%2s %2s              %s     %s     %s     %s     %s     %s     %s     %d     %s     %s     %d\n" % (1, "ME", "M", "M", "E", "R", "S", "C", "R", 1, "G", "S", 2))
                file.write("@N MANAGEMENT  PLANT IRRIG FERTI RESID HARVS\n")
                file.write("%2s %2s              %s     %s     %s     %s     %s\n" % (1, "MA", "R", self.irrsim, "R", "R", "R"))
#                 file.write("%2s %2s              %s     %s     %s     %s     %s\n" % (1, "MA", "R", self.irrsim, "A", "R", "R"))
                file.write("@N OUTPUTS     FNAME OVVEW SUMRY FROPT GROUT CAOUT WAOUT NIOUT MIOUT DIOUT VBOSE CHOUT OPOUT\n")
                file.write("%2s %2s              %s     %s     %s     %d     %s     %s     %s     %s     %s     %s     %s     %s     %s\n" % (1, "OU", "N", "Y", "Y", 1, "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y"))
                
                #Automatic Management
                file.write('\n@  AUTOMATIC MANAGEMENT\n')
                file.write('@N PLANTING    PFRST PLAST PH2OL PH2OU PH2OD PSTMX PSTMN\n')
                file.write(' 1 PL            001   001    40   100    30    40    10\n')
                file.write('@N IRRIGATION  IMDEP ITHRL ITHRU IROFF IMETH IRAMT IREFF\n')
                file.write(' 1 IR             30    50   100 GS000 IR004    25     1\n')
                file.write('@N NITROGEN    NMDEP NMTHR NAMNT NCODE NAOFF\n')
                file.write(' 1 NI             30    50    25 FE001 GS000\n')
                file.write('@N RESIDUES    RIPCN RTIME RIDEP\n')
                file.write(' 1 RE            100     1    20\n')
                file.write('@N HARVEST     HFRST HLAST HPCNP HPCNR\n')
                file.write(' 1 HA              0   001   100     0\n')
                file.close()
                return
            
class Irrigation(object):
    """
    This class is for creating irrigation management data for a season
    """
    def __init__(self, mo = 5, d = 1, method = "IR004", amt = 10, nwyr = 'yes'):
        
        self.mo = mo
        self.d = d
        self.method = method
        self.amt = amt
        self.nwyr = nwyr
        
        irr = pd.read_csv('IrrSched.csv')
        if self.nwyr == 'yes':
            with open('IrrSched.csv', 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, lineterminator = '\n')
                writer.writerow(['MONTH','DAY','ROP','VAL'])
                writer.writerow(("%d" % (self.mo),"%d" % (self.d), "%5s" % (self.method), "%d" % (self.amt)))
        else:
            with open('IrrSched.csv', 'a', newline = '') as csvfile:
                writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, lineterminator = '\n')
                writer.writerow(("%d" % (self.mo),"%d" % (self.d), "%5s" % (self.method), "%d" % (self.amt)))
        csvfile.close()
        
class Fertilizer(object):
    """
    This class is for creating irrigation management data for a season
    """
    def __init__(self, mo =5, d = 1, fmat = 'FE001', fapp = 'AP006', fdep = 5, famn = 10, famp = 0, famk = 0, famc = -99, famo = -99, focd = -99, fername = -99, nwyr = 'yes'):
       
        self.mo = mo
        self.d = d
        self.fmat = fmat
        self.fapp = fapp
        self.fdep = fdep
        self.famn = famn
        self.famp = famp
        self.famk = famk
        self.famc = famc
        self.famo = famo
        self.focd = focd
        self.fername = fername
        self.nwyr = nwyr
        
        if self.nwyr == 'yes':
            with open('FertSched.csv', 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, lineterminator = '\n')
                writer.writerow(['MONTH','DAY','FMCD','FACD','FDEP','FAMN','FAMP','FAMK','FAMC','FAMO','FOCD','FERNAME'])
                writer.writerow(("%d" % (self.mo),"%d" % (self.d), "%5s"%(self.fmat), "%5s"%(self.fapp), "%d"%(self.fdep), "%d"%(self.famn), "%d"%(self.famp), "%d"%(self.famk), "%d"%(self.famc), "%d"%(self.famo), "%d"%(self.focd), "%d"%(self.fername)))
        else:
            with open('FertSched.csv', 'a') as csvfile:
                writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, lineterminator = '\n')
                writer.writerow(("%d" % (self.mo),"%d" % (self.d), "%5s"%(self.fmat), "%5s"%(self.fapp), "%d"%(self.fdep), "%d"%(self.famn), "%d"%(self.famp), "%d"%(self.famk), "%d"%(self.famc), "%d"%(self.famo), "%d"%(self.focd), "%d"%(self.fername)))
        csvfile.close()
        
class Organic(object):
    def __init__(self, mo=4,d=15,mat='RE003',amt=10,n=70,p=15,k=15,met='AP004'):
        self.mo=mo
        self.d=d
        self.mat=mat
        self.amt=amt
        self.n=n
        self.p=p
        self.k=k
        self.met=met
        with open('OrgSched.csv', 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, lineterminator = '\n')
            writer.writerow(['MONTH','DAY','RCOD','RAMT','RESN','RESP','RESK','RMET'])
            writer.writerow(("%d" % (self.mo),"%d" % (self.d), "%5s" % (self.mat), "%d" % (self.amt), "%d" % (self.n),"%d"%(self.p),"%d"%(self.k),"%5s"%(self.met)))
        csvfile.close()
        
class Tillage(object):
    """
    This class is for specifying tillage management data for a season
    """
    def __init__(self, mo =4, d = 15, imp = "TI011", depth = 10, name = -99):
        
        self.mo = mo
        self.d = d
        self.imp = imp
        self.depth = depth
        self.name = name
        
        with open('TillSched.csv', 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, lineterminator = '\n')
            writer.writerow(['MONTH','DAY','TIMPL','TDEP','TNAME'])
            writer.writerow(("%d" % (self.mo),"%d" % (self.d), "%5s" % (self.imp), "%d" % (self.depth), "%d" % (self.name)))
        csvfile.close()
        
class Chemicals(object):
    """
    This is a class specifying chemical management data for the DSSAT_yield.py wrapper
    """
    def __init__(self, mo =4, d = 15, mat = 'CH009', amt = 10, method = 'AP006', depth = 10, target = -99, name = -99, nwyr = 'yes'):
        
        self.mo = mo
        self.d = d
        self.mat = mat
        self.amt = amt
        self.method = method
        self.depth = depth
        self.target = target
        self.name = name
        self.nwyr = nwyr
        
        if self.nwyr == 'yes':
            with open('ChemSched.csv', 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, lineterminator = '\n')
                writer.writerow(['MONTH','DAY','CHCOD','CHAMT','CHME','CHDEP','CHT','CHNAME'])
                writer.writerow(("%d" % (self.mo),"%d" % (self.d), "%5s" % (self.mat), "%d" % (self.amt), "%5s" % (self.method), "%d" % (self.depth), "%d" % (self.target), "%d" % (self.name)))
        else:
            with open('ChemSched.csv', 'a') as csvfile:
                writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, lineterminator = '\n')
                writer.writerow(("%d" % (self.mo),"%d" % (self.d), "%5s" % (self.mat), "%d" % (self.amt), "%5s" % (self.method), "%d" % (self.depth), "%d" % (self.target), "%d" % (self.name)))
        csvfile.close()

class DSSATModel(object):
    def __init__(self, mode = 'B', batchfile = 'run.v46', ofile = 'output.OUT'):
        self.mode = mode
        self.batchfile = batchfile
        self.ofile = ofile
        
    def Run(self):
        os.system('DSCSM046.exe %s %s > %s'%(self.mode, self.batchfile, self.ofile))
        file = open("Summary.OUT", 'r')
        r = file.readlines()[-1].split()
        file.close()
        y = int(r[20])
        i = int(r[29])
        return y, i




'''
#Standard hybrid for Mead,NE will be GDD2600
# org = [0,1000,2000,3000,4000,5000,6000,7000,8000]
# pop = [10.0]
c = 'GDD2600' # options are "medium", "pioneer", and GDD2600 (Heeren et al, 2007)
fert = [0,150,300]
for f in fert:
#     Organic(mo=5,d=1,mat='RE003',amt=r,n=1,p=0,k=0,met='AP004')
    Fertilizer(mo=5,d=1,fmat='FE004',fapp='AP003',fdep=10,famn=f,famp=0,famk=0,famc=-99,famo=-99,focd=-99,fername=-99,nwyr='yes')
    ds = DSSATFile(cultivar = c,soil='Loam',weather='UNME', st_yr=2015, plant_month=5, plant_date=1, ppop=10.0, pmeth='S', row_space=75, pdepth=5, mode = 'B', irrsim='A')
    ds.Batch()
    ds.Control()
    dm = DSSATModel()
    dm.Run()
    file = open("Summary.OUT", 'r')
    r = file.readlines()[-1].split()
    file.close()
    y = int(r[20])
    i = int(r[29])
    print(y,i)
'''

'''
PPOP SCENARIO ANALYSIS ON YIELD
import win32com.client
xl = win32com.client.Dispatch('Excel.Application')
xl.Visible = True
wb = xl.Workbooks.Add()
ws = wb.Worksheets.Add()
i=2
nfert = [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,600]
for n in nfert:
    Fertilizer(mo =5, d = 1, fmat = 'FE004', fapp = 'AP003', fdep = 10, famn = n, famp = 0, famk = 0, famc = -99, famo = -99, focd = -99, fername = -99, nwyr = 'yes')
    ds = DSSATFile(irrsim='A',st_yr=2015,ppop=5.0)
    ds.Batch()
    ds.Control()
    model = DSSATModel()
    model.Run()
    file = open('Summary.OUT','r')
    r = file.readlines()[-1].split()
    y=r[19]
    ws.Range('A1').Value = ds.ppop
    ws.Range('A%s'%(i)).Value = n
    ws.Range('B%s'%(i)).Value = y
    i+=1
'''

     
'''
# VERIFICATION OF BASELINE SCENARIO
nfert  = [200]
for n in nfert:
    Fertilizer(mo =5, d = 1, fmat = 'FE004', fapp = 'AP003', fdep = 10, famn = n, famp = 0, famk = 0, famc = -99, famo = -99, focd = -99, fername = -99, nwyr = 'yes')
    ds = DSSATFile()
    ds.Batch()
    ds.Control()
    model = DSSATModel()
    model.Run()
    file = open('Summary.OUT','r')
    r = file.readlines()[-1].split()
    print(r[19])
'''


