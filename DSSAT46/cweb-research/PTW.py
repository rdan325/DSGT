'''
Module for calculating PTW results for each category of interest
'''

class E85():
# E85 PTW pathway uses SI ICEV - EtOH FFV    
    def __init__(self, energy):
        
        self.co2 = energy*70.46
        self.ch4 = energy*.00175
        self.n2o = energy*.00108
        self.bio = -energy*30
        self.voc = energy*.02591
        self.co  = energy*.57
        self.nox = energy*.02442
        self.ghg = self.co2+self.ch4*23+self.n2o*296+self.bio

class Gas():
# E10 PTW pathway uses SI ICEV - E10
    def __init__(self, energy):
        
        # Using SI ICEV: E10 vehicle pathway
        self.co2 = energy*71.73
        self.ch4 = energy*.00017
        self.n2o = energy*.00108
        self.bio = 0
        self.voc = energy*.02591
        self.co  = energy*.57
        self.nox = energy*.02442
        self.ghg = self.co2+self.ch4*23+self.n2o*296+self.bio
        
# e = 116540
# print(E85(e).ghg-Gas(e).ghg)


 