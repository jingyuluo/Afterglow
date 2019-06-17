import ROOT
import sys
import os
import argparse
import json
from math import sqrt
import array

parser=argparse.ArgumentParser()
#parser.add_argument("-h",  "--help", help="Print these messages.")
parser.add_argument("-d",  "--dir",  default="",  help="Directory where derived corrections with type 2 only are located.")
parser.add_argument("-o",  "--output", default="", help="The output directory")
parser.add_argument("-f",  "--file", default="",  help="File of derived corrections is located.")
parser.add_argument("-l",  "--label",default="",  help="Append the names of output files with this label.")
parser.add_argument("-j",  "--json", default="",  help="Certification JSON file for selecting runs.")
parser.add_argument("-r",  "--reweight", default=False, action="store_true", help="Using the reweight factor for FPix only data")
args=parser.parse_args()


ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(ROOT.kTRUE)


def CorrSBIL(x):
    return (6.40042-2.00959*x+1.34069*x*x-0.431342*x*x*x)*x

runSelection={}
if args.json !="":
    certfile=open(args.json)
    runSelection=json.load(certfile)
    certfile.close()

filenames=[]
if args.dir!="":
    shortfilenames=os.listdir(args.dir)

    for shortfilename in shortfilenames:
        if shortfilename.find("Overall_")!=-1:
            filenames.append(args.dir+"/"+shortfilename)
if args.file!="":
    filenames.append(args.file)
#Fill   Bfield    Runs 
LBInfo={}

LBInfo["4647"]=["3.798513298",[262325,262326,262327,262328]]
LBInfo["4643"]=["3.798513298",[262270,262271,262272,262273,262274,262275,262277]]
LBInfo["4640"]=["3.798513298",[262248,262249,262250,262252,262253,262254]]
LBInfo["4639"]=["3.798513298",[262235]]
LBInfo["4638"]=["3.798513298",[262204,262205]]
LBInfo["4634"]=["3.798513298",[262081,262114,262121,262137,262147,262156,262157,262163,262164,262165,262167,262168,262169,262170,262171,262172,262173,262174]]
LBInfo["4569"]=["3.798970769",[260627]]
LBInfo["4565"]=["3.798970769",[260593]]
LBInfo["4562"]=["3.798970769",[260575,260576,260577]]
LBInfo["4560"]=["1.544083541",[260488,260489,260490,260491,260492,260493,260496,260497,260498,260499,260510,260527,260528,260532,260533,260534,260536,260538,260540,260541]]
LBInfo["4557"]=["3.719991773",[260424,260425,260426,260427,260431,260433,260439]]
LBInfo["4555"]=["3.80020411",[260373]]
LBInfo["4545"]=["0.019018997",[260230,260232,260233,260234,260235]]
LBInfo["4540"]=["0.019018997",[260099,260100,260101,260102,260104,260105,260107,260108,260114,260119,260132,260135,260136]]
LBInfo["4538"]=["0.019018997",[260034,260035,260036,260037,260038,260039,260041,260043,260061,260062,260066]]
LBInfo["4536"]=["0.019018997",[259968,259971,259972,259973]]
LBInfo["4532"]=["3.800569273",[259884,259890,259891]]
LBInfo["4530"]=["3.800569273",[259861,259862]]
LBInfo["4528"]=["3.800569273",[259809,259810,259811,259812,259813,259817,259818,259820,259821,259822]]
LBInfo["4525"]=["3.800569273",[259721]]
LBInfo["4522"]=["3.800569273",[259681,259682,259683,259685,259686]]
LBInfo["4519"]=["3.800569273",[259636,259637]]
LBInfo["4518"]=["3.800569273",[259626]]
LBInfo["4513"]=["3.800569273",[259464]]
LBInfo["4511"]=["3.800569273",[259429,259431]]
LBInfo["4510"]=["3.800569273",[259399]]
LBInfo["4509"]=["3.800569273",[259384,259385,259388]]
LBInfo["4505"]=["3.800569273",[259351,259352,259353]]
LBInfo["4499"]=["3.800569273",[259236,259237]]
LBInfo["4496"]=["3.800569273",[259199,259200,259201,259202,259204,259205,259207,259208]]
LBInfo["4495"]=["3.800569273",[259152,259157,259158,259159,259161,259162,259163,259164,259167]]
LBInfo["4485"]=["3.800569273",[258741,258742,258745,258749,258750]]
LBInfo["4479"]=["3.800569273",[258702,258703,258705,258706,258712,258713,258714]]
LBInfo["4477"]=["3.800569273",[258694]]
LBInfo["4476"]=["3.800569273",[258655,258656]]
LBInfo["4467"]=["3.800569273",[258425,258426,258427,258428,258432,258434,258440,258442,258443,258444,258445,258446,258448]]
LBInfo["4466"]=["3.800569273",[258403]]
LBInfo["4464"]=["3.799768191",[258335]]
LBInfo["4463"]=["3.799768191",[258312,258313,258319,258320]]
LBInfo["4462"]=["3.799768191",[258287]]
LBInfo["4455"]=["3.799768191",[258211,258213,258214,258215]]
LBInfo["4452"]=["3.799768191",[258174,258175,258177]]
LBInfo["4449"]=["3.799768191",[258157,258158,258159]]
LBInfo["4448"]=["3.799768191",[258129,258136]]
LBInfo["4444"]=["3.799768191",[257968,257969]]
LBInfo["4440"]=["3.799768191",[257804,257805,257816,257818,257819,257821,257822,257823,257824,257825]]
LBInfo["4437"]=["3.799768191",[257750,257751]]
LBInfo["4435"]=["3.799768191",[257721,257722,257723,257725,257732,257733,257734,257735]]
LBInfo["4434"]=["3.799768191",[257682]]
LBInfo["4432"]=["3.799768191",[257645]]
LBInfo["4428"]=["3.799768191",[257613,257614]]
LBInfo["4426"]=["3.799768191",[257599]]
LBInfo["4423"]=["3.799768191",[257531]]
LBInfo["4420"]=["3.799768191",[257487,257490]]
LBInfo["4418"]=["3.799768191",[257461]]
LBInfo["4410"]=["3.799768191",[257394,257395,257396,257397,257398,257399,257400]]
LBInfo["4402"]=["1.68653331",[257027,257032,257035,257038,257042,257044,257055,257058,257059]]
LBInfo["4398"]=["3.799673444",[256936,256941]]
LBInfo["4397"]=["3.799673444",[256926]]
LBInfo["4393"]=["3.799673444",[256866,256867,256868,256869]]
LBInfo["4391"]=["3.799673444",[256842,256843]]
LBInfo["4386"]=["3.799673444",[256801]]
LBInfo["4384"]=["3.799673444",[256728,256729,256730,256733,256734]]
LBInfo["4381"]=["3.799673444",[256673,256674,256675,256676,256677]]
LBInfo["4376"]=["3.799673444",[256630]]
LBInfo["4364"]=["0.018967839",[256464]]
LBInfo["4363"]=["0.018967839",[256443,256444,256445,256446,256447,256448]]
LBInfo["4360"]=["0.018967839",[256423,256424]]
LBInfo["4356"]=["0.018967839",[256405,256406]]
LBInfo["4349"]=["0.018967839",[256347,256348,256349,256350,256353,256355]]
LBInfo["4342"]=["0.018967839",[256245]]
LBInfo["4341"]=["0.018967839",[256234,256235,256236,256237]]
LBInfo["4337"]=["0.018967839",[256214,256215,256216,256217]]
LBInfo["4332"]=["0.018967839",[256167,256168,256169,256171]]
LBInfo["4323"]=["0.018967839",[256001,256002,256003,256004]]
LBInfo["4322"]=["0.018967839",[255981,255982,255983,255984,255985,255986,255987,255988,255989,255990,255993]]
LBInfo["4269"]=["3.799233459",[255019,255029,255030,255031]]
LBInfo["4268"]=["3.799233459",[255003]]
LBInfo["4266"]=["3.799233459",[254980,254982,254983,254984,254985,254986,254987,254989,254991,254992,254993]]
LBInfo["4257"]=["3.799233459",[254914]]
LBInfo["4256"]=["3.799233459",[254905,254906,254907]]
LBInfo["4254"]=["3.799233459",[254879]]
LBInfo["4249"]=["3.799233459",[254852]]
LBInfo["4246"]=["3.799233459",[254833]]
LBInfo["4243"]=["3.799233459",[254790]]
LBInfo["4231"]=["0.019004049",[254608]]
LBInfo["4225"]=["0.019004049",[254532]]
LBInfo["4224"]=["0.019004049",[254512]]
LBInfo["4220"]=["0.019004049",[254437,254450,254451,254453,254454,254455,254456,254457,254458,254459]]
LBInfo["4219"]=["0.019004049",[254416]]
LBInfo["4214"]=["0.019004049",[254380]]
LBInfo["4212"]=["0.019004049",[254362,254364,254366,254367,254368]]
LBInfo["4211"]=["0.019004049",[254349]]
LBInfo["4210"]=["0.019004049",[254340,254341,254342]]
LBInfo["4208"]=["0.019004049",[254332]]
LBInfo["4207"]=["0.019004049",[254306,254307,254308,254309,254310,254313,254314,254315,254316,254317,254318,254319]]
LBInfo["4205"]=["1.151918971",[254280,254282,254283,254284,254285,254289,254290,254292,254293,254294]]
LBInfo["4201"]=["3.800328948",[254227,254229,254230,254231,254232]]
LBInfo["4020"]=["0.018957838",[252126]]
LBInfo["4019"]=["0.018957838",[252116]]
LBInfo["4008"]=["3.799702722",[251883]]
LBInfo["4006"]=["3.799702722",[251864]]
LBInfo["4001"]=["3.799702722",[251781]]
LBInfo["3996"]=["3.799702722",[251717,251718,251721]]
LBInfo["3992"]=["3.799702722",[251636,251638,251640,251642,251643]]
LBInfo["3988"]=["3.799702722",[251559,251560,251561,251562]]
LBInfo["3986"]=["3.799702722",[251548]]
LBInfo["3983"]=["3.799702722",[251521,251522,251523]]
LBInfo["3981"]=["2.849426279",[251491,251493,251496,251497,251498,251499,251500]]
LBInfo["3976"]=["3.799731187",[251244,251249,251250,251251,251252]]
LBInfo["3974"]=["3.799731187",[251131,251134,251142,251143,251147,251149,251150,251153,251155,251156,251160,251161,251162,251163,251164,251167,251168,251170]]
LBInfo["3971"]=["3.799731187",[251022,251023,251024,251025,251026,251027,251028]]
LBInfo["3965"]=["0.018936371",[250930,250931,250932]]
LBInfo["3962"]=["0.036359372",[250885,250886,250889,250890,250891,250892,250893,250895,250896,250897,250898,250899,250901,250902]]
LBInfo["3960"]=["0.018828806",[250862,250863,250864,250865,250866,250867,250868,250869,250871]]
LBInfo["3858"]=["0.018828806",[248025,248026,248027,248028,248029,248030,248031,248032,248033,248035,248036,248037,248038]]
LBInfo["3857"]=["0.018828806",[247981,247982,247983,247987,247989,247990,247991,247992,247994,247996,247998,248000,248002,248003,248004,248005,248006,248007,248009]]
LBInfo["3855"]=["0.018828806",[247910,247911,247912,247913,247914,247915,247917,247919,247920,247921,247923,247924,247926,247927,247928,247931,247933,247934]]
LBInfo["3851"]=["0.018828806",[247702,247703,247704,247705,247707,247708,247710,247711,247716,247718,247719,247720]]
LBInfo["3850"]=["0.018828806",[247685]]
LBInfo["3848"]=["0.018828806",[247642,247644,247646,247647,247648]]
LBInfo["3847"]=["0.018828806",[247623]]
LBInfo["3846"]=["0.018828806",[247607,247609,247610,247611,247612]]
LBInfo["3835"]=["0.018828806",[247377,247379,247380,247381,247382,247383,247384,247385,247386,247387,247388,247389,247394,247395,247397,247398]]
LBInfo["3833"]=["0.018828806",[247302,247303,247305,247306,247307,247309,247310,247313,247317,247318,247319,247320,247323,247324,247326,247328,247333,247334,247335,247336]]
LBInfo["3829"]=["0.018828806",[247231,247232,247233,247234,247235,247236,247237,247238,247240,247241,247243,247244,247245,247246,247247,247248,247250,247251,247252,247253,247255,247256,247259,247261,247262,247263,247265,247266,247267]]
LBInfo["3824"]=["0.018828806",[247068,247069,247070,247073,247076,247077,247078,247079,247081]]
LBInfo["3820"]=["0.018842477",[246951,246953,246954,246956,246957,246958,246959,246960,246961,246962,246963]]
LBInfo["3819"]=["0.0188423",[246908,246912,246913,246914,246919,246920,246923,246926,246930,246933,246934,246936]]

def GetGaussianMeanError(hist):
    fun1 = ROOT.TF1("fun1", "gaus", -0.03, 0.1)
    hist.Fit(fun1, "R")
    MeanError=[fun1.GetParameter(1), fun1.GetParameter(2)]
    return MeanError

def GetMeanError(hist):
    MeanError = [hist.GetMean(), hist.GetMeanError()]
    return MeanError

def findRunInFill(run):
    for LB in LBInfo:
        if int(run) in LBInfo[LB][1]:
            return LB


if args.json !="":
    LBSelection=[]
    for run in runSelection:
        thisLB=findRunInFill(run)
        if thisLB not in LBSelection:
            LBSelection.append(thisLB)
    LBSelection.sort()




hists={}
#corrhists={}
can=ROOT.TCanvas("can","",1000,700)
if args.label!="":
    outRootFileName="systematicHistograms_"+args.dir+"_"+args.label+".root"
    outCVSFileName="summary_"+args.dir+"_"+args.label+".csv"
else:
    outRootFileName="systematicHistograms_"+args.dir+".root"
    outCVSFileName="summary_"+args.dir+".csv"
    
oFile=ROOT.TFile(args.output+"/"+outRootFileName,"RECREATE")
newfile=ROOT.TFile(args.output+"/type2minitree_"+args.label+".root", "RECREATE")
newtree=ROOT.TTree("minitree", "minitree")

FILL = array.array('I', [0])
RUN = array.array( 'I', [0])
LS  = array.array( 'I', [0])
type1frac = array.array( 'd', [0])
type2frac = array.array( 'd', [0])
overalltype1 = array.array( 'd', [0])
overallratio = array.array( 'd', [0])
AveSBIL = array.array('d', [0])
noisefrac = array.array('d', [0])
type1frac_err = array.array('d', [0])
type2frac_err = array.array('d', [0])
AveSBIL_corr = array.array('d', [0])

NBX    = array.array('I', [0])

newtree.Branch("FILL", FILL, "FILL/I")
newtree.Branch("RUN", RUN, "RUN/I")
newtree.Branch("LS", LS, "LS/I")
newtree.Branch("type2frac", type2frac, "type2frac/D")
newtree.Branch("type1frac", type1frac, "type1frac/D")
newtree.Branch("overalltype1", overalltype1, "overalltype1/D")
newtree.Branch("overallratio", overallratio, "overallratio/D")
newtree.Branch("AveSBIL", AveSBIL, "AveSBIL/D")
newtree.Branch("noisefrac", noisefrac, "noisefrac/D")
newtree.Branch("AveSBIL_corr", AveSBIL_corr, "AveSBIL_corr/D")
newtree.Branch("type1frac_err", type1frac_err, "type1frac_err/D")
newtree.Branch("type2frac_err", type2frac_err, "type2frac_err/D")

newtree.Branch("NBX", NBX, "NBX/I")

csvSummary=open(outCVSFileName,"w+")
type1ValueError={}
type1ValueErrorClean={}
#corrValue={}
type2ValueError={}
type2ValueErrorClean={}
type2RMS={}
type2RMSClean={}
AverageSBIL={}
OverallRatioperLB = {}
overallratiovalue = {}
NBXperLB = {}
FillsperLB = {}
NoiseperLB = {}
Type1CorrperLB = {}

filenames.sort()

nCount=0
nClean=0
for filename in filenames:
    try:
        tfile=ROOT.TFile.Open(filename)
        #thisfill = int(filename.split(".")[0][-4:])
        #print "this fill", thisfill
        f1keys=tfile.GetListOfKeys()
    except:
        continue
    
    fHistNames=[]
    corrHistNames={} 
    for f1key in f1keys:
        if f1key.GetName().find("After_Corr_")!=-1:
            fHistNames.append(f1key.GetName())
        #if f1key.GetName().find("Overall_Ratio_")!=-1:
        #    corrLB=f1key.GetName().split("_")[2]+"_"+f1key.GetName().split("_")[3]
        #    corrHistNames[corrLB]=f1key.GetName() 
    print fHistNames
    for fHistName in fHistNames:
        tfile.cd() 
        #print fHistName
        #thisRun=fHistName.split("_")[2]
        #thisLB=findRunInFill(thisRun)
        thisLB=fHistName.split("_")[2]+"_"+fHistName.split("_")[3]+"_"+fHistName.split("_")[4]
        noisehist = "Noise_"+fHistName.split("_")[2]+"_"+fHistName.split("_")[3]+"_"+fHistName.split("_")[4]+"_"+fHistName.split("_")[5]
        Overallratio = "Overall_Ratio_"+fHistName.split("_")[2]+"_"+fHistName.split("_")[3]+"_"+fHistName.split("_")[4]+"_"+fHistName.split("_")[5]
        #type1overall = "Overall_type1_"+fHistName.split("_")[2]+"_"+fHistName.split("_")[3]+"_"+fHistName.split("_")[4]
        FillsperLB[thisLB] = int(fHistName.split("_")[5].lstrip("Fill"))
        #if args.json!="":

        #if thisLB not in LBSelection:
        #if thisLB!="4947":
        #    continue

        
        hists[fHistName]=tfile.Get(fHistName)
        h_noise = tfile.Get(noisehist)
        #h_type1 = tfile.Get(type1overall)
        NoiseperLB[thisLB] = h_noise.GetBinContent(2)
        OverallRatioperLB[thisLB] = tfile.Get(Overallratio)
        overallratiovalue[thisLB] =  OverallRatioperLB[thisLB].GetBinContent(2)
        Type1CorrperLB[thisLB] = 1.0#1-h_type1.GetBinContent(2)
        #corrhists[fHistName]=tfile.Get(corrHistNames[thisLB])
        oFile.cd() 
        print hists[fHistName].Integral()
        if hists[fHistName].Integral() < 0.0000005*3600:
            print "Histogram contains only data from noise... skipping"
            continue
        
        hists[fHistName+"SBIL"]=ROOT.TH1F(fHistName+"SBIL", "; SBIL;"+fHistName,100, -0.5, 8)
        
        hists[fHistName+"TrailingRatios"]=ROOT.TH1F(fHistName+"TrailingRatios",";Type 1 Fraction from after BX train;"+fHistName,270,-0.06,0.15)
        hists[fHistName+"Type2Residuels"]=ROOT.TH1F(fHistName+"Type2Residuels",";Type 2 residual (Hz/ub);"+fHistName,200,-0.02,0.15)
        
        lastBX=-1
        lastBXlumi=-1
        nActiveBX=0
        total_Lumi=0
        for ibx in range(2,hists[fHistName].GetNbinsX()-2):

            
            lumiM1=hists[fHistName].GetBinContent(ibx-1)
            lumi=hists[fHistName].GetBinContent(ibx)
            lumiP1=hists[fHistName].GetBinContent(ibx+1)
            lumiP2=hists[fHistName].GetBinContent(ibx+2)
            lumiP3=hists[fHistName].GetBinContent(ibx+3)
            lumiP4=hists[fHistName].GetBinContent(ibx+4)
            lumiP5=hists[fHistName].GetBinContent(ibx+5)
            hists[fHistName+"SBIL"].Fill(lumi)
            # Is bunch active?
            # Needs to be more than noise and less than lumi
            threshold=hists[fHistName].GetMaximum()*0.2
            if lumi>threshold: 
                nActiveBX=nActiveBX+1
                total_Lumi+=lumi
                # is leading?
                #if lumiM1<threshold:
                # is last active bx?
                #if lumiP1<threshold:# and lumiP2<threshold: next is non-active
                if lumiP1<threshold and lumiP2<threshold: # end of train
                    lastBX=ibx
                    lastBXlumi=lumi
                    hists[fHistName+"TrailingRatios"].Fill(lumiP1/lumi-lumiP2/lumi)#((lumiP1-(lumiP2+lumiP3+lumiP4)/3)/lumi)
                    #print ibx,lumiP1,lumi,lumiP1/lumi, (lumiP1-(lumiP2+lumiP3+lumiP4)/3)/lumi
            
            # how is type 2 doing?
            # from 2 bx beyond a train to 30 or next active BX
            if lastBX>0 and ibx-lastBX>1 and ibx-lastBX<30 and lumi<threshold:
                hists[fHistName+"Type2Residuels"].Fill(lumi/lastBXlumi)

        if nActiveBX==0:
            print "No active BXs in",fHistName
            AverageSBIL[thisLB]=0
            continue
        Ave_Lumi = float(total_Lumi)/float(nActiveBX)
        AverageSBIL[thisLB]=Ave_Lumi
        NBXperLB[thisLB] = nActiveBX
        can.cd()
        hists[fHistName+"TrailingRatios"].Draw()
        #hists[fHistName+"TrailingRatios"].Write()
        can.Update()
        #print "means",hists[fHistName+"TrailingRatios"].GetMean()
        #print "stdev",hists[fHistName+"TrailingRatios"].GetRMS()
        
    
        hists[fHistName+"Type2Residuels"].Draw()
        #hists[fHistName+"Type2Residuels"].Write()
        can.Update()
        #print "Type2 residuels",hists[fHistName+"Type2Residuels"].GetMean()
        #print "Type2 resid RMS",hists[fHistName+"Type2Residuels"].GetRMS()
   
        #print GetGaussianMeanError(hists[fHistName+"TrailingRatios"])
        type1MeanError = GetMeanError(hists[fHistName+"TrailingRatios"])
        csvSummary.write(fHistName+","+str(type1MeanError[0])+","+str(type1MeanError[1])+","+str(hists[fHistName+"Type2Residuels"].GetMean())+","+str(hists[fHistName+"Type2Residuels"].GetRMS())+"\n")
       
        if not type1ValueError.has_key(thisLB):
            type1ValueError[thisLB]={}
            type1ValueErrorClean[thisLB]={}
                
        if not type2ValueError.has_key(thisLB):
            type2ValueError[thisLB]={}
            type2ValueErrorClean[thisLB]={}
            type2RMS[thisLB]={}
            type2RMSClean[thisLB]={}
        nCount=nCount+1
        type1ValueError[thisLB][fHistName]=[hists[fHistName+"TrailingRatios"].GetMean(),hists[fHistName+"TrailingRatios"].GetMeanError()]#type1MeanError#[hists[fHistName+"TrailingRatios"].GetMean(),hists[fHistName+"TrailingRatios"].GetMeanError()]
        type2ValueError[thisLB][fHistName]=[hists[fHistName+"Type2Residuels"].GetMean(),hists[fHistName+"Type2Residuels"].GetMeanError()]
        type2RMS[thisLB][fHistName]=sqrt(hists[fHistName+"Type2Residuels"].GetMean()*hists[fHistName+"Type2Residuels"].GetMean()+hists[fHistName+"Type2Residuels"].GetRMS()*hists[fHistName+"Type2Residuels"].GetRMS())
        #corrValue[thisLB]=corrhists[fHistName].GetBinContent(2)
        #if hists[fHistName+"TrailingRatios"].GetMeanError() <0.005 and hists[fHistName+"Type2Residuels"].GetMeanError()<0.00050 and hists[fHistName+"Type2Residuels"].GetMeanError()!=0:
        #    if hists[fHistName+"TrailingRatios"].GetMean()<-0.04:
        #        #print fHistName+"TrailingRatios is",hists[fHistName+"TrailingRatios"].GetMean(),"looks dubious... skipping... need better criteria for skipping"
        #        continue
        type2ValueErrorClean[thisLB][fHistName]=[hists[fHistName+"Type2Residuels"].GetMean(),hists[fHistName+"Type2Residuels"].GetMeanError()]
        type2RMSClean[thisLB][fHistName]=sqrt(hists[fHistName+"Type2Residuels"].GetMean()*hists[fHistName+"Type2Residuels"].GetMean()+hists[fHistName+"Type2Residuels"].GetRMS()*hists[fHistName+"Type2Residuels"].GetRMS())
        type1ValueErrorClean[thisLB][fHistName]=[hists[fHistName+"TrailingRatios"].GetMean(),hists[fHistName+"TrailingRatios"].GetMeanError()]#type1MeanError#[hists[fHistName+"TrailingRatios"].GetMean(),hists[fHistName+"TrailingRatios"].GetMeanError()]
        nClean=nClean+1
        #if hists[fHistName+"Type2Residuels"].GetMeanError() <0.005 :
        #hists[fHistName+"TrailingRatios"].Write()
        #hists[fHistName+"Type2Residuels"].Write()


csvSummary.write("\n\n")

oFile.cd() 
type1OverTime={}
type1OverTimeClean={}
LBs=type1ValueError.keys()
type2OverTime={}
type2OverTimeClean={}
type2RMSOverTime={}
type2RMSOverTimeClean={}
LBs=type2ValueError.keys()
LBs.sort()
labels1=";Blocks of 50 LSs;Type 1 Fraction"
labels2=";Blocks of 50 LSs;Type 2 SBIL"
labels3=";Blocks of 50 LSs;Type 2 SBIL RMS"
type1OverTime["all"]=ROOT.TH1F("type1OverTimeAll",labels1,nCount,0,nCount)
type1OverTimeClean["all"]=ROOT.TH1F("type1OverTimeCleanAll",labels1,nClean,0,nClean)
type2OverTime["all"]=ROOT.TH1F("type2OverTimeAll",labels2,nCount,0,nCount)
type2OverTimeClean["all"]=ROOT.TH1F("type2OverTimeCleanAll",labels2,nClean,0,nClean)
type2RMSOverTime["all"]=ROOT.TH1F("type2RMSOverTimeAll", labels3,nCount,0,nCount)
type2RMSOverTimeClean["all"]=ROOT.TH1F("type2RMSOverTimeCleanAll", labels3, nClean, 0, nClean)


tgraph1=ROOT.TGraphErrors()
tgraph2=ROOT.TGraphErrors()
tgraph3=ROOT.TGraphErrors()
tgraph4=ROOT.TGraphErrors()
tgraph5=ROOT.TGraphErrors()
tgraph6=ROOT.TGraphErrors()
#corrgraph=ROOT.TGraphErrors()
protype1=ROOT.TProfile("type1fracVsSBIL", ";Average SBIL (Hz/#muB); Type 1 residual (Fraction)", 100, 1, 9, -0.5, 0.5)

tgraph1.SetTitle(";Lumi Blocks;Type 1 residual (Fraction)")
tgraph2.SetTitle(";Lumi Blocks;Type 2 residual (SBIL,Hz/#mub)")
tgraph3.SetTitle(";Lumi Blocks;Type 2 residual RMS (SBIL,Hz/#mub)")
tgraph4.SetTitle(";Average SBIL (Hz/#muB); Type 1 residual (Fraction)")
tgraph5.SetTitle(";Average SBIL (Hz/#muB); Type 2 residual (SBIL, Hz/#mub)")
tgraph6.SetTitle(";Average SBIL (Hz/#muB); Type 2 Fraction")
#corrgraph.SetTitle(";Lumi Blocks; Overalll correction factor")
tgraph1.SetName("type1FracPerLB")
tgraph2.SetName("type2SBILPerLB")
tgraph3.SetName("type2SBILRMSPerLB")
tgraph4.SetName("type1FracvsSBIL")
tgraph5.SetName("type2SBILvsSBIL")
tgraph6.SetName("type2FracvsSBIL")
#corrgraph.SetName("corrfacPerLB")

iFill=0

overlapLBs=[]

iCountAll=1
iCleanAll=1

xsec_scale=1

LBToRunLS=[]
if args.reweight:
    xsec_scale=2.6

for LB in LBs:
    type1OverTime[LB]=ROOT.TH1F("type1OverTime"+str(LB),labels1,len(type1ValueError[LB]),0,len(type1ValueError[LB]))
    type2OverTime[LB]=ROOT.TH1F("type2OverTime"+str(LB),labels2,len(type2ValueError[LB]),0,len(type2ValueError[LB]))
    type2RMSOverTime[LB]=ROOT.TH1F("type2RMSOverTime"+str(LB), labels3, len(type2RMS[LB]),0,len(type2RMS[LB]))
    LSBlockNames=type1ValueError[LB].keys()
    LSBlockNames.sort()
    iCount=1
    for LSBlock in LSBlockNames:
        type1OverTime[LB].SetBinContent(iCount,type1ValueError[LB][LSBlock][0])
        type1OverTime[LB].SetBinError(iCount,type1ValueError[LB][LSBlock][1])
        type2OverTime[LB].SetBinContent(iCount,type2ValueError[LB][LSBlock][0])
        type2OverTime[LB].SetBinError(iCount,type2ValueError[LB][LSBlock][1])
        type2RMSOverTime[LB].SetBinContent(iCount, type2RMS[LB][LSBlock])
        iCount=iCount+1
    
        type1OverTime["all"].SetBinContent(iCountAll,type1ValueError[LB][LSBlock][0])
        type1OverTime["all"].SetBinError(iCountAll,type1ValueError[LB][LSBlock][1])
        type2OverTime["all"].SetBinContent(iCountAll,type2ValueError[LB][LSBlock][0])
        type2OverTime["all"].SetBinError(iCountAll,type2ValueError[LB][LSBlock][1])
        type2RMSOverTime["all"].SetBinContent(iCountAll, type2RMS[LB][LSBlock])
        iCountAll=iCountAll+1
    
    type1OverTimeClean[LB]=ROOT.TH1F("type1OverTimeClean"+str(LB),labels1,len(type1ValueErrorClean[LB]),0,len(type1ValueErrorClean[LB]))
    type2OverTimeClean[LB]=ROOT.TH1F("type2OverTimeClean"+str(LB),labels2,len(type2ValueErrorClean[LB]),0,len(type2ValueErrorClean[LB]))
    type2RMSOverTimeClean[LB]=ROOT.TH1F("type2RMSOverTimeClean"+str(LB),labels3,len(type2RMSClean[LB]), 0,len(type2RMSClean[LB]))
    
    LSBlockNames=type1ValueErrorClean[LB].keys()
    LSBlockNames.sort()
    iCount=1
    for LSBlock in LSBlockNames:
        type1OverTimeClean[LB].SetBinContent(iCount,type1ValueErrorClean[LB][LSBlock][0])
        type1OverTimeClean[LB].SetBinError(iCount,type1ValueErrorClean[LB][LSBlock][1])
        type2OverTimeClean[LB].SetBinContent(iCount,type2ValueErrorClean[LB][LSBlock][0])
        type2OverTimeClean[LB].SetBinError(iCount,type2ValueErrorClean[LB][LSBlock][1])
        type2RMSOverTimeClean[LB].SetBinContent(iCount, type2RMSClean[LB][LSBlock])
        iCount=iCount+1

        type1OverTimeClean["all"].SetBinContent(iCleanAll,type1ValueErrorClean[LB][LSBlock][0])
        type1OverTimeClean["all"].SetBinError(iCleanAll,type1ValueErrorClean[LB][LSBlock][1])
        type2OverTimeClean["all"].SetBinContent(iCleanAll,type2ValueErrorClean[LB][LSBlock][0])
        type2OverTimeClean["all"].SetBinError(iCleanAll,type2ValueErrorClean[LB][LSBlock][1])
        type2RMSOverTimeClean["all"].SetBinContent(iCleanAll, type2RMSClean[LB][LSBlock])
        iCleanAll=iCleanAll+1

        
    can.Update()
    type1OverTime[LB].Draw()
    can.Update()
    type1OverTimeClean[LB].Draw()
    fitType="pol0"
    type1OverTimeClean[LB].Fit(fitType,"QS")
    fitResult1=type1OverTimeClean[LB].GetFunction(fitType)
    type2OverTimeClean[LB].Fit(fitType,"QS")
    fitResult2=type2OverTimeClean[LB].GetFunction(fitType)
    type2RMSOverTimeClean[LB].Fit(fitType,"QS")
    fitResult3=type2RMSOverTimeClean[LB].GetFunction(fitType)
    #if corrValue[LB]>1:
    #            overlapLBs.append(LB)
    try:
        value1=fitResult1.GetParameter(0)
        error1=fitResult1.GetParError(0)
        value2=fitResult2.GetParameter(0)
        error2=fitResult2.GetParError(0)
        value3=fitResult3.GetParameter(0)
        #print LB,value1,error1,value2,error2
        if error1<0.01: #and int(LB)>4220:
            LBToRunLS.append([iFill, LB]) 
            tgraph1.SetPoint(iFill,iFill,value1)
            tgraph1.SetPointError(iFill,0,error1)
            tgraph2.SetPoint(iFill,iFill,value2)
            tgraph2.SetPointError(iFill,0,error2)
            tgraph3.SetPoint(iFill,iFill,value3)
            tgraph4.SetPoint(iFill,AverageSBIL[LB]*xsec_scale,value1)
            tgraph4.SetPointError(iFill, 0, error1)
            tgraph5.SetPoint(iFill,AverageSBIL[LB]*xsec_scale,value2)
            tgraph5.SetPointError(iFill, 0, error2)
            tgraph6.SetPoint(iFill,AverageSBIL[LB]*xsec_scale,value2/AverageSBIL[LB])
            #corrgraph.SetPoint(iFill,iFill,corrValue[LB])
            protype1.Fill(AverageSBIL[LB], value1)
            FILL[0] = FillsperLB[LB]
            RUN[0] = int(LB.split("_")[0])
            LS[0] = int(LB.split("_")[1].lstrip("LS"))
            type1frac[0] = value1
            type2frac[0] = value2
            overalltype1[0] = Type1CorrperLB[LB]
            overallratio[0] = overallratiovalue[LB] 
            AveSBIL[0] = AverageSBIL[LB]
            noisefrac[0] = NoiseperLB[LB]/(NoiseperLB[LB]+AverageSBIL[LB])
            AveSBIL_corr[0] = CorrSBIL(AverageSBIL[LB])
            type1frac_err[0] = error1
            type2frac_err[0] = error2
            NBX[0]  = NBXperLB[LB]
            #print RUN[0], LS[0], type2frac[0]
            newtree.Fill()
            iFill=iFill+1
            print "FILLING TGRAPHS",iFill
            if value1<-0.01:
                print "LARGE TYPE 1 OUTLIER"
        iCount=iCount+1
        csvSummary.write(str(LB)+","+str(fitResult1.GetParameter(0))+","+str(fitResult1.GetParError(0))+"\n")
    except:
        print LB,"giveup"

    can.Update()
    type2OverTime[LB].Draw()
    can.Update()
    type2OverTimeClean[LB].Draw()
    can.Update()
    type2RMSOverTime[LB].Draw()
    can.Update()
    type2RMSOverTimeClean[LB].Draw()
    

can.SetTickx()
can.SetTicky()
text=ROOT.TLatex(0.72,0.92,"2017  (13TeV)")
text.SetNDC()
text.SetTextFont(62)
text.SetTextSize(0.05)
text2=ROOT.TLatex(0.15,0.92,"CMS #bf{#scale[0.75]{#it{Preliminary}}}")
text2.SetNDC()
text2.SetTextSize(0.05)
text2.SetTextFont(62)

type1OverTime["all"].Draw()
type1OverTimeClean["all"].Draw()
type2OverTime["all"].Draw()
type2OverTimeClean["all"].Draw()

tgraph1.GetYaxis().SetRangeUser(-0.01, 0.04)
tgraph1.GetYaxis().SetTitleOffset(1.0)
tgraph1.SetMarkerStyle(23)
tgraph1.SetMarkerSize(1)
tgraph1.SetMarkerColor(ROOT.kBlue)
tgraph1.Draw("AP")
text.Draw("same")
text2.Draw("same")
can.Update()
can.SaveAs(args.output+"/type1_residualPerLB_"+args.label+".png")
can.SaveAs(args.output+"/type1_residualPerLB_"+args.label+".C")

tgraph2.GetYaxis().SetTitleOffset(1.3)
tgraph2.SetMarkerStyle(23)
tgraph2.SetMarkerSize(1)
tgraph2.SetMarkerColor(ROOT.kBlue)
tgraph2.Draw("AP")
text.Draw("same")
text2.Draw("same")
can.Update()
can.SaveAs(args.output+"/type2_residualPerLB_"+args.label+".png")
can.SaveAs(args.output+"/type2_residualPerLB_"+args.label+".C")

tgraph3.GetYaxis().SetTitleOffset(1.3)
tgraph3.SetMarkerStyle(23)
tgraph3.SetMarkerSize(1)
tgraph3.SetMarkerColor(ROOT.kBlue)
tgraph3.Draw("AP")
text.Draw("SAME")
text2.Draw("SAME")
can.Update()
can.SaveAs(args.output+"/type2_residualRMSPerLB_"+args.label+".png")
can.SaveAs(args.output+"/type2_residualRMSPerLB_"+args.label+".C")


tgraph4.GetYaxis().SetRangeUser(-0.03, 0.04)
tgraph4.GetYaxis().SetTitleOffset(1.3)
tgraph4.SetMarkerStyle(23)
tgraph4.SetMarkerSize(1)
tgraph4.SetMarkerColor(ROOT.kBlue)
tgraph4.Draw("AP")
text.Draw("SAME")
text2.Draw("SAME")
can.Update()
can.SaveAs(args.output+"/type1_residualvsSBIL_PerLB_"+args.label+".png")
can.SaveAs(args.output+"/type1_residualvsSBIL_PerLB_"+args.label+".C")


protype1.GetYaxis().SetTitleOffset(1.3)
protype1.SetMarkerStyle(23)
protype1.SetMarkerSize(1)
protype1.SetMarkerColor(ROOT.kBlue)
protype1.GetYaxis().SetRangeUser(-0.01, 0.04)
protype1.Fit("pol1","","",2, 8)
protype1.Draw("P")
text.Draw("SAME")
text2.Draw("SAME")
can.Update()
can.SaveAs(args.output+"/protype1_residualvsSBIL_PerLB_"+args.label+".png")
can.SaveAs(args.output+"/protype1_residualvsSBIL_PerLB_"+args.label+".C")

tgraph5.GetYaxis().SetTitleOffset(1.3)
tgraph5.SetMarkerStyle(23)
tgraph5.SetMarkerSize(1)
tgraph5.SetMarkerColor(ROOT.kBlue)
tgraph5.Draw("AP")
text.Draw("SAME")
text2.Draw("SAME")
can.Update()
can.SaveAs(args.output+"/type2_residualvsSBIL_PerLB_"+args.label+".png")
can.SaveAs(args.output+"/type2_residualvsSBIL_PerLB_"+args.label+".C")

tgraph6.GetYaxis().SetTitleOffset(1.3)
tgraph6.SetMarkerStyle(23)
tgraph6.SetMarkerSize(1)
tgraph6.SetMarkerColor(ROOT.kBlue)
tgraph6.Draw("AP")
text.Draw("SAME")
text2.Draw("SAME")
can.Update()
can.SaveAs(args.output+"/type2frac_residualvsSBIL_PerLB_"+args.label+".png")
can.SaveAs(args.output+"/type2frac_residualvsSBIL_PerLB_"+args.label+".C")

#corrgraph.GetYaxis().SetTitleOffset(1.3)
#corrgraph.SetMarkerStyle(23)
#corrgraph.SetMarkerSize(1)
#corrgraph.SetMarkerColor(ROOT.kBlue)
#corrgraph.Draw("AP")
#text.Draw("SAME")
#text2.Draw("SAME")
#can.Update()
#can.SaveAs("corrfactor_PerLB_"+args.label+".png")
#can.SaveAs("corrfactor_PerLB_"+args.label+".C")

protype1.Write()
tgraph1.Write()
tgraph2.Write()
tgraph3.Write()
tgraph4.Write()
tgraph5.Write()
tgraph6.Write()

print LBToRunLS
print "Overlap LBs:", overlapLBs
oFile.Write()
oFile.Close()
newfile.WriteTObject(newtree, "newtree")
