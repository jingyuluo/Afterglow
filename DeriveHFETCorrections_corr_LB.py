import sys, os
from math import exp
import argparse
import subprocess
import ROOT
import array

parser=argparse.ArgumentParser()
#parser.add_argument("-h", "--help", help="Display this message.")
parser.add_argument("-f", "--file", default="", help="The path to a cert tree.")
parser.add_argument("-d", "--dir",  default="", help="The path to a directory of cert trees.")
parser.add_argument("-r", "--runs", default="", help="Comma separated list of runs.")
parser.add_argument("--auto", default=False, action="store_true", help="Determine the runs from the certtree")
parser.add_argument("-l", "--label", default="", help="The label for outputs")
parser.add_argument('-b', '--batch',   action='store_true', default=False, help="Batch mode (doesn't make GUI TCanvases)")
parser.add_argument('--nLSInLumiBlock', default=50, type=int, help="Number of LSs to group")
parser.add_argument('-a', '--all', action='store_true', default=False, help="Store all the data into a single hist")

BXLength=3564
zeroes = array.array('d', [0.]*BXLength)
args=parser.parse_args()

def findRange( hist, cut):
    gaplist=[]
    for i in range(1,3600):
        if hist.GetBinContent(i)<cut:
            gaplist.append(i)
    return gaplist

ROOT.gStyle.SetOptStat(0)
if args.batch is True:
    ROOT.gROOT.SetBatch(ROOT.kTRUE)


#corrTemplate=ROOT.TH1F("corrTemplate","",3600,0,3600)

#corrTemplate.SetBinContent(1,a+b*exp(c))
#for i in range(1,3600):
#    corrTemplate.SetBinContent(i,b*exp(-(i-2)*c))
#corrTemplate.GetXaxis().SetRangeUser(0,100)

filename=args.file
if args.runs!="":
    runs=args.runs.split(",")
else:
    runs=[]
label=args.label


#templatefile=ROOT.TFile("/afs/cern.ch/work/j/jingyu/CMSSW_8_0_5/src/PCCTools/PCLumiProd/HFET_template.root")
#h_template = templatefile.Get("h_template")
#corrTemplate = h_template.Clone()

newfile=ROOT.TFile("Overall_Correction_"+label+".root", "recreate")

tfile=ROOT.TFile(filename)
tree=tfile.Get("certtree")

tree.SetBranchStatus("*",0)
tree.SetBranchStatus("fill*", 1)
tree.SetBranchStatus("run*", 1)
tree.SetBranchStatus("LS*", 1)

runtoFills = {}
maxLSInRun={}

if args.auto:
    nentries=tree.GetEntries()

    for iev in range(nentries):
        tree.GetEntry(iev)
        if str(tree.run) not in runs:
            print "Adding",tree.run
            runs.append(str(tree.run))
            runtoFills[str(tree.run)] = str(tree.fill)

        if not maxLSInRun.has_key(str(tree.run)):
            maxLSInRun[str(tree.run)] = tree.LS
        elif maxLSInRun[str(tree.run)]<tree.LS:
            maxLSInRun[str(tree.run)]=tree.LS

    print "auto", runs
    runs.sort()


allLumiPerBX={}
normPerBX={}
allCorrLumiPerBX={}
Noiseslumi = {}
allLumiAfterNoiseSubPerBX={}
tempType1Res={}
corrRatioOverall={}
LBKeys=[]

tree.SetBranchStatus("run*", 1)
tree.SetBranchStatus("LS*", 1)
tree.SetBranchStatus("HFETLumi_perBX*", 1)
tree.SetBranchStatus("HFETBXid*",1)
tree.SetBranchStatus("nBXHFET*", 1)

for run in runs:
    runnum=int(run)

    for iLB in range(maxLSInRun[run]/args.nLSInLumiBlock+1):
        
        if maxLSInRun[run]<15:
            continue
        LBKey=run+"_LS"+str(iLB*args.nLSInLumiBlock+1)+"_LS"+str((iLB+1)*args.nLSInLumiBlock)+"_Fill"+runtoFills[run]
        if iLB==maxLSInRun[run]/args.nLSInLumiBlock:
            LBKey=run+"_LS"+str(iLB*args.nLSInLumiBlock+1)+"_LS"+str(maxLSInRun[run])+"_Fill"+runtoFills[run]
        LBKeys.append(LBKey)
        normPerBX[LBKey] = ROOT.TH1F("normPerBX"+LBKey, "", BXLength, 0, BXLength)
        allLumiPerBX[LBKey]=ROOT.TH1F("allLumiPerBX"+LBKey, "", BXLength, 0, BXLength)
        allCorrLumiPerBX[LBKey]=ROOT.TH1F
        Noiseslumi[LBKey] = ROOT.TH1F("noiselumi"+LBKey, "", 10, 0, 10)
        allLumiAfterNoiseSubPerBX[LBKey] = ROOT.TH1F
        tempType1Res[LBKey] = ROOT.TH1F("tempType1Res"+LBKey, "", 310, -0.06, 0.25)
        corrRatioOverall[LBKey]=ROOT.TH1F("corrRatioOverall"+LBKey,"",10,0,10)
    #histnoise=ROOT.TH1F("histnoise","",3600,0,3600)
    #histfull=ROOT.TH1F("histfull","",3600,0,3600)
    #normfull=ROOT.TH1F("normfull","",3600,0,3600)
    #corrfill=ROOT.TH1F("corrfill","",3600,0,3600)

LBKeys.sort()

nentries=tree.GetEntries()

for iev in range(nentries):

    if iev%1000==101:
        print "event", iev
    tree.GetEntry(iev)
    if str(tree.run) not in runs:
        continue
    iLB = (tree.LS-1)/args.nLSInLumiBlock
    LBKey = str(tree.run)+"_LS"+str(iLB*args.nLSInLumiBlock+1)+"_LS"+str((iLB+1)*args.nLSInLumiBlock)+"_Fill"+str(tree.fill)
    if iLB==(maxLSInRun[str(tree.run)]/args.nLSInLumiBlock):
        LBKey=str(tree.run)+"_LS"+str(iLB*args.nLSInLumiBlock+1)+"_LS"+str(maxLSInRun[str(tree.run)])+"_Fill"+str(tree.fill)
    if not LBKey in LBKeys:
        continue
    #if tree.LS<3700 and tree.fill==runnum and tree.run==274344:
    #    if tree.LS>84 and tree.LS<100:
    #        continue
    #    if tree.LS>114 and tree.LS<130:
    #        continue
    #    if tree.LS>279 and tree.LS<295:
    #        continue
    #    if tree.LS>384 and tree.LS<400:
    #        continue
    #    if tree.LS>632:
    #        continue
    for ibx in range(tree.nBXHFET):
        #print tree.HFETLumi_perBX[ibx]
        if not args.all:
            allLumiPerBX[LBKey].Fill(tree.HFETBXid[ibx], tree.HFETLumi_perBX[ibx])
            normPerBX[LBKey].Fill(tree.HFETBXid[ibx], 1)
        else:
            allLumiPerBX[LBKeys[0]].Fill(tree.HFETBXid[ibx], tree.HFETLumi_perBX[ibx])
            normPerBX[LBKeys[0]].Fill(tree.HFETBXid[ibx], 1)

for LBKey in LBKeys:
    #print allLumiPerBX.keys()
    allLumiPerBX[LBKey].Divide(normPerBX[LBKey])
    allLumiPerBX[LBKey].SetError(zeroes)
    allCorrLumiPerBX[LBKey]=allLumiPerBX[LBKey].Clone()
    noise=0
    nbx=0
    maxlumi = allCorrLumiPerBX[LBKey].GetMaximum()
    for ibx in range(1, 50):
        if allCorrLumiPerBX[LBKey].GetBinContent(ibx)>maxlumi*0.2:
            continue
        noise+=allCorrLumiPerBX[LBKey].GetBinContent(ibx)
        nbx+=1
    noise = noise/float(nbx)
    
    for ibx in range(BXLength):
        allCorrLumiPerBX[LBKey].SetBinContent(ibx, allCorrLumiPerBX[LBKey].GetBinContent(ibx)-noise)

    allLumiAfterNoiseSubPerBX[LBKey] = allCorrLumiPerBX[LBKey].Clone()
    for ino in range(10):
        Noiseslumi[LBKey].SetBinContent(ino, noise)

    threshold = allCorrLumiPerBX[LBKey].GetMaximum()*0.2
    for ibx in range(2, allCorrLumiPerBX[LBKey].GetNbinsX()-5):

        lumiM1 = allCorrLumiPerBX[LBKey].GetBinContent(ibx-1)
        lumi = allCorrLumiPerBX[LBKey].GetBinContent(ibx)
        lumiP1 = allCorrLumiPerBX[LBKey].GetBinContent(ibx+1)
        lumiP2 = allCorrLumiPerBX[LBKey].GetBinContent(ibx+2)
        lumiP3 = allCorrLumiPerBX[LBKey].GetBinContent(ibx+3)
        lumiP4 = allCorrLumiPerBX[LBKey].GetBinContent(ibx+4)
        lumiP5 = allCorrLumiPerBX[LBKey].GetBinContent(ibx+5)

        if lumi>threshold and lumiP1<threshold and lumiP2<threshold:
            tempType1Res[LBKey].Fill((lumiP1-(lumiP3+lumiP4+lumiP5)/3)/lumi)#allCorrLumiPerBX[LBKey].GetBinContent(ibx))

    meanType1 = tempType1Res[LBKey].GetMean()

    for k in range(1,BXLength):
        bin_k = allCorrLumiPerBX[LBKey].GetBinContent(k)
        allCorrLumiPerBX[LBKey].SetBinContent(k+1, allCorrLumiPerBX[LBKey].GetBinContent(k+1)-bin_k*meanType1)

    activelumi_before = 0
    activelumi_after = 0

    for ibx in range(1, BXLength):
        if(allLumiPerBX[LBKey].GetBinContent(ibx)>allLumiPerBX[LBKey].GetMaximum()*0.2):
            activelumi_before+=allLumiPerBX[LBKey].GetBinContent(ibx)
            activelumi_after+=allCorrLumiPerBX[LBKey].GetBinContent(ibx)
    if not activelumi_before==0:
        corr_ratio=activelumi_after/activelumi_before
    else:
        corr_ratio=0

    for i in range(1, 10):
        corrRatioOverall[LBKey].SetBinContent(i, corr_ratio)
    print "Finish up dividing plots"



    allLumiPerBX[LBKey].SetTitle("Random Triggers in Run "+LBKey+";BX;Average PCC SBIL Hz/ub")
    
    allCorrLumiPerBX[LBKey].SetTitle("Random Triggers in Run "+LBKey+", after correction;BX; Average PCC SBIL Hz/ub")
    allLumiPerBX[LBKey].SetLineColor(416)
    #ratio_noise.Divide(corrfill)

    newfile.WriteTObject(allLumiPerBX[LBKey],  "Before_Corr_"+LBKey)
    newfile.WriteTObject(allCorrLumiPerBX[LBKey], "After_Corr_"+LBKey)
    newfile.WriteTObject(Noiseslumi[LBKey], "Noise_"+LBKey)
    newfile.WriteTObject(allLumiAfterNoiseSubPerBX[LBKey], "After_NoiseCorr_"+LBKey)
    newfile.WriteTObject(corrRatioOverall[LBKey], "Overall_Ratio_"+LBKey)
    newfile.WriteTObject(tempType1Res[LBKey], "tempType1Res_"+LBKey)
