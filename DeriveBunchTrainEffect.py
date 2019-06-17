import ROOT
import sys
import os
import argparse
import json
from math import sqrt
import array

parser=argparse.ArgumentParser()
parser.add_argument("--hfoc", default="", help="The file for the hfoc luminosity")
parser.add_argument("--hfet", default="", help="The file for the hfet luminosity")

args = parser.parse_args()

ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(ROOT.kTRUE)


ocfile = ROOT.TFile.Open(args.hfoc)
etfile = ROOT.TFile.Open(args.hfet)

outfile = ROOT.TFile("test_output_overall_vs_leadoc.root", "RECREATE")
newtree = ROOT.TTree("newtree", "newtree")

FILL = array.array('I', [0])
RUN = array.array('I', [0])
LS = array.array('I', [0])
AveSBIL = array.array('d', [0])
doubleratio = array.array('d', [0])


newtree.Branch("FILL", FILL, "FILL/I")
newtree.Branch("RUN", RUN, "RUN/I")
newtree.Branch("LS", LS, "LS/I")
newtree.Branch("AveSBIL", AveSBIL, "AveSBIL/D")
newtree.Branch("doubleratio", doubleratio, "doubleratio/D")

fockeys = ocfile.GetListOfKeys()
fetkeys = etfile.GetListOfKeys()

focHistNames = []
foc_LBtoHistNames = {}
fetHistNames = []
fet_LBtoHistNames = {}



for fockey in fockeys:
    if fockey.GetName().find("After_Corr_")!=-1:
        focHistNames.append(fockey.GetName())

for fetkey in fetkeys:
    if fetkey.GetName().find("After_Corr_")!=-1:
        fetHistNames.append(fetkey.GetName())


print focHistNames
for focHistName in focHistNames:
    ocfile.cd()

    thisLB = focHistName.split("_")[2]+"_"+focHistName.split("_")[3]+"_"+focHistName.split("_")[5]
    foc_LBtoHistNames[thisLB] = focHistName

for fetHistName in fetHistNames:
    etfile.cd()

    thisLB = fetHistName.split("_")[2]+"_"+fetHistName.split("_")[3]+"_"+fetHistName.split("_")[5]
    fet_LBtoHistNames[thisLB] = fetHistName


for LB in foc_LBtoHistNames.keys():
    if fet_LBtoHistNames.has_key(LB):
        histoc = ocfile.Get(foc_LBtoHistNames[LB])
        histet = etfile.Get(fet_LBtoHistNames[LB])
         
        maxlumi = histoc.GetMaximum()
        threshold = maxlumi*0.2
        
        sum_leadoc = 0
        sum_leadet = 0
        sum_trainoc = 0
        sum_trainet = 0
        
        n_train = 0

        for ibx in range(2, histoc.GetNbinsX()-2):

            lumiM1 = histoc.GetBinContent(ibx-1)
            lumi   = histoc.GetBinContent(ibx)
            lumiP1 = histoc.GetBinContent(ibx+1)
            lumiP2 = histoc.GetBinContent(ibx+2)
            lumiP3 = histoc.GetBinContent(ibx+3)
            lumiP4 = histoc.GetBinContent(ibx+4)

            if lumiM1<threshold and lumi > threshold and lumiP1 > threshold and lumiP2 > threshold and lumiP3 > threshold and lumiP4 > threshold:
                lumiet   = histet.GetBinContent(ibx)   
                lumietP1 = histet.GetBinContent(ibx+1)
                lumietP2 = histet.GetBinContent(ibx+2)
                lumietP3 = histet.GetBinContent(ibx+3)
                lumietP4 = histet.GetBinContent(ibx+4)


                sum_leadoc += lumi
                sum_trainoc += (lumiP1+lumiP2+lumiP3+lumiP4)/4
                sum_leadet += lumiet
                sum_trainet += (lumietP1+lumietP2+lumietP3+lumietP4)/4
                n_train+=1
        try:
            FILL[0] = int(LB.split("_")[2].lstrip("Fill"))
            RUN[0] = int(LB.split("_")[0])
            LS[0] = int(LB.split("_")[1].lstrip("LS"))
            AveSBIL[0] = float(sum_leadoc)/n_train
            doubleratio[0] = (float(sum_trainet)/float(sum_trainoc))/(float(sum_leadet)/float(sum_leadoc))
            newtree.Fill()
        except:
            print "problem with LB, ibx", LB, ibx
            print sum_leadoc, sum_leadet, sum_trainoc, sum_trainet

outfile.WriteTObject(newtree, "newtree")
outfile.Close()
