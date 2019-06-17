import ROOT
import sys,os
import numpy
import array
import math
import argparse
import pickle
import time

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--pccfile', type=str, default="", help='The pccfile to input (pixel clusters and vertices)')
parser.add_argument('--brilfile', type=str, default="brildata", help='bril data is here')
parser.add_argument('--nobril', default=False, action="store_true", help="Don\'t process bril data (default false)")
parser.add_argument('--beamonly', default=False, action="store_true", help="BRIL data only contains beam info")
parser.add_argument('-l','--label',type=str,default="",  help="Label for output file")
parser.add_argument('--minfill', type=int, default=3818, help="Minimum fill number")
parser.add_argument('--minrun',  type=int, default=230000,help="Minimum run number")
parser.add_argument('--isBatch', default=False, action="store_true", help="Doesn't pop up plots and only fills tree when CMS and BRIL data are present")
parser.add_argument('-v', '--includeVertices', default=True, action="store_false", help="Include vertex counting (default true)")
parser.add_argument('--eventBased', default=False, action="store_true", help="PCC ntuples are event based (default false--typically LS-based)")
parser.add_argument('--collisionType', default="pp13TeV", help="Key for xsec (default: pp13TeV)")
parser.add_argument('--vetoListFile', default="", help="File with list of modules to veto")
parser.add_argument('--outPath', default="", help="The path for the output file")
#parser.add_argument('-#-perBX', type=bool, default=False, action="store_true", help="Store PC lumi per BX")
#                if args.perBX:

args = parser.parse_args()

if args.nobril:
    args.brilfile=""

vetoList=[302126344,  302123024,  302122768,  302057496,  302123804,  302124308, 302126364,  302188820]
if args.vetoListFile!="":
    try:
        vlFile=open(args.vetoListFile)
        vetoList=[]
        for line in vlFile.readlines():
            try:
                vetoList.append(int(line))
            except:
                print "Can't parse",line
    except:
        print "Failed to read veto list file",args.vetoListFile
        sys.exit(0)


f_LHC = 11245.6
t_LS=math.pow(2,18)/f_LHC
xsec_ub=80000. #microbarn


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


weightThreshold=1e-5

# the value is already summed over weight
def AverageWithWeight(list):
    sumValue=0
    sumWeight=0
    for value,weight in list:
        sumValue=sumValue+value
        sumWeight=sumWeight+weight

    if sumWeight>0:
        return float(sumValue)/sumWeight

def GetWeightedValues(list):
    count=0
    sumOfWeights=0
    sumOfWeights2=0
    weightedSum=0

    for value,weight in list:
        #print value,weight
        if weight<weightThreshold:
            continue
        count=count+1
        sumOfWeights=sumOfWeights+weight
        sumOfWeights2=sumOfWeights2+math.pow(weight,2)
        weightedSum=weightedSum+weight*value

    return count,sumOfWeights,sumOfWeights2,weightedSum


def GetMean(list):
    #print "list length",len(list)
    count,sumOfWeights,sumOfWeights2,weightedSum=GetWeightedValues(list)
    mean=GetMeanFromWeightedValues(sumOfWeights,weightedSum)
    return mean


def GetMeanFromWeightedValues(sumOfWeights,weightedSum):
    mean=0
    if sumOfWeights>0:
        mean=weightedSum/sumOfWeights
    return mean


def GetMeanAndMeanError(list):
    count,sumOfWeights,sumOfWeights2,weightedSum=GetWeightedValues(list)
    if sumOfWeights2==0:
        return -99,-99
    neff=math.pow(sumOfWeights,2)/sumOfWeights
    mean=GetMeanFromWeightedValues(sumOfWeights,weightedSum)

    #print neff,count,sumOfWeights
    
    weightedSumDiffFromAve2=0
    for value,weight in list:
        if weight<weightThreshold:
            continue
        weightedSumDiffFromAve2=weightedSumDiffFromAve2+weight*math.pow(value-mean,2) 

    stddev=0
    meanError=0
    if count>2:
        stddev=math.sqrt( weightedSumDiffFromAve2 / (sumOfWeights))
        meanError=stddev/math.sqrt(neff)

    #print "stddev",stddev

    return mean,meanError



startTime=time.time()
onlineLumi={} #(fill,run,LS)
runInfo={}

if not args.nobril:
    fileName=args.brilfile
    print fileName,"this dict size",
    if fileName.find(".pkl") !=-1:
        try:
            filePath=fileName
            pklFile=open(filePath,'rb')
            data=pickle.load(pklFile)
            print len(data),
            if data.has_key("runInfo"):
                for runInfoKey in data["runInfo"]:
                    if not runInfo.has_key(runInfoKey):
                        runInfo[runInfoKey]={}
                    runInfo[runInfoKey].update(data["runInfo"][runInfoKey])
            onlineLumi.update(data)
            pklFile.close()
        except:
            print "Problem with pickle file",

    print " new total LSs: ",len(onlineLumi)
#print onlineLumi
print runInfo

endTime=time.time()
print "Duration: ",endTime-startTime

maxLS={}
    
goodVertexCounts={}
tightVertexCounts={}
validVertexCounts={}
PCCsPerLayerBXPerLS={}
PCCsPerLS={}
eventRates={}
timeStamps={}
nBXs={}
lumiEstimate={}
# key is bx,LS and LS

if args.outPath!="":
    outpath=args.outPath
    
    #if outpath.find("/store")==0:
    #    outpath="root://eoscms//eos/cms"+outpath

if args.pccfile!="":
    filename=args.pccfile

    if filename.find("/store")==0: # file is in eos
        filename="root://eoscms//eos/cms"+filename
    
    tfile=ROOT.TFile.Open(filename)
    
    tree=tfile.Get("lumi/tree")
    
    tree.SetBranchStatus("*",0)
    if args.includeVertices:
        tree.SetBranchStatus("nGoodVtx*",1)
        tree.SetBranchStatus("nTightVtx*", 1)
        tree.SetBranchStatus("nValidVtx*",1)
    tree.SetBranchStatus("run*",1)
    tree.SetBranchStatus("LS*",1)
    tree.SetBranchStatus("event*",1)
    tree.SetBranchStatus("timeStamp_begin*", 1)
    tree.SetBranchStatus("nPixelClusters*",1)
    tree.SetBranchStatus("layer*",1)
    tree.SetBranchStatus("BXNo",1)

    nentries=tree.GetEntries()
      
    for iev in range(nentries):
        print iev
        tree.GetEntry(iev)
        if iev%1000==0:
            print "iev,",iev
            print "(tree.run,tree.LS)",tree.run,tree.LS
            print "len(tree.nPixelClusters)",len(tree.nPixelClusters)
            print "len(tree.layers)",len(tree.layers)
        if len(tree.nPixelClusters)==0:
            continue
        
        LSKey=(tree.run,tree.LS)
        eventRates[LSKey]=tree.eventCounter/23.31
        timeStamps[LSKey]=tree.timeStamp_begin
        nBXs[LSKey]=len(tree.BXNo)
        if args.includeVertices:
            if LSKey not in goodVertexCounts:
                goodVertexCounts[LSKey]=[]
                goodVertexCounts[LSKey].append([])
                goodVertexCounts[LSKey].append({})

                tightVertexCounts[LSKey]=[]
                tightVertexCounts[LSKey].append([])
                tightVertexCounts[LSKey].append({})

                validVertexCounts[LSKey]=[]
                validVertexCounts[LSKey].append([])
                validVertexCounts[LSKey].append({})

                for bx,counts in tree.BXNo:
                    goodVertexCounts[LSKey][1][bx]=[]
                    tightVertexCounts[LSKey][1][bx]=[]
                    validVertexCounts[LSKey][1][bx]=[]
    
            for ibx,nGoodVtx in tree.nGoodVtx:
                goodVertexCounts[LSKey][0].append([nGoodVtx,tree.BXNo[ibx]])
                goodVertexCounts[LSKey][1][ibx].append([nGoodVtx,tree.BXNo[ibx]])

            for ibx,nTightVtx in tree.nTightVtx:
                tightVertexCounts[LSKey][0].append([nTightVtx, tree.BXNo[ibx]])
                tightVertexCounts[LSKey][1][ibx].append([nTightVtx, tree.BXNo[ibx]])

            for ibx,nValidVtx in tree.nValidVtx:
                validVertexCounts[LSKey][0].append([nValidVtx,tree.BXNo[ibx]])
                validVertexCounts[LSKey][1][ibx].append([nValidVtx,tree.BXNo[ibx]])
               
       
        #for ibx in tree.BXNo:
        #    print "BXNo", ibx[0], ibx[1]
       
        # 0 is the total count for layers 2-5
        # 1-5 is the count for layre 1-5
        # 6 is the count for per BX

        PCCsPerEntry={}
        PCCsPerLayerBX={}
        bxids=[]
        if PCCsPerEntry.has_key((tree.run,tree.LS)) == 0:
            PCCsPerEntry[(tree.run,tree.LS)]=[0]*10
            PCCsPerEntry[(tree.run,tree.LS)].append({}) # for bx->counts
       
        if PCCsPerLS.has_key((tree.run,tree.LS)) == 0:
            PCCsPerLS[(tree.run,tree.LS)]=[[] for x in xrange(10)]
            PCCsPerLS[(tree.run,tree.LS)].append({})
        
  
        if PCCsPerLayerBX.has_key((tree.run, tree.LS))==0:
            PCCsPerLayerBX[(tree.run, tree.LS)]=[{} for x in xrange(10)]
    
        if PCCsPerLayerBXPerLS.has_key((tree.run, tree.LS))==0:
            PCCsPerLayerBXPerLS[(tree.run, tree.LS)]=[{} for x in xrange(10)]   
 
        if not maxLS.has_key(tree.run):
            maxLS[tree.run]=0
        
        if tree.LS>maxLS[tree.run]:
            maxLS[tree.run]=tree.LS+5
    
        layerNumbers=[]
        for item in tree.layers:
            layerNumbers.append(item[1])
    
        counter=0
        bxid=-1
        for item in tree.nPixelClusters:
            bxid=item[0][0]
            module=item[0][1]
            layer=tree.layers[module]
            clusters=item[1]
   
            if module in vetoList:
                continue

            #if layer==6:
            #    layer=1
            
            print "layer:", layer 
            PCCsPerEntry[(tree.run,tree.LS)][layer]=PCCsPerEntry[(tree.run,tree.LS)][layer]+clusters
            if not PCCsPerEntry[(tree.run,tree.LS)][10].has_key(bxid):
                PCCsPerEntry[(tree.run,tree.LS)][10][bxid]=0
            for Layer in range(5):
                if not PCCsPerLayerBX[(tree.run, tree.LS)][Layer].has_key(bxid):
                    PCCsPerLayerBX[(tree.run, tree.LS)][Layer][bxid]=0
            #if layer!=1:
            PCCsPerEntry[(tree.run,tree.LS)][10][bxid]=PCCsPerEntry[(tree.run,tree.LS)][10][bxid]+clusters
            PCCsPerEntry[(tree.run,tree.LS)][0]=PCCsPerEntry[(tree.run,tree.LS)][0]+clusters
            if layer>0 and layer<6:
                PCCsPerLayerBX[(tree.run, tree.LS)][layer-1][bxid]=PCCsPerLayerBX[(tree.run, tree.LS)][layer-1][bxid]+clusters
    
            if bxid not in bxids:
               bxids.append(bxid)
        counter=counter+1
  
        if not args.eventBased: #divide by the sum of events
            PCCsPerEntry[(tree.run,tree.LS)][0]=PCCsPerEntry[(tree.run,tree.LS)][0]/float(tree.eventCounter)
            for layer in range(1,6):
                PCCsPerEntry[(tree.run,tree.LS)][layer]=PCCsPerEntry[(tree.run,tree.LS)][layer]/float(tree.eventCounter)
            for bxid in bxids:
                PCCsPerEntry[(tree.run,tree.LS)][10][bxid]=PCCsPerEntry[(tree.run,tree.LS)][10][bxid]/float(tree.BXNo[bxid])
                for Layer in range(5):
                    PCCsPerLayerBX[(tree.run, tree.LS)][Layer][bxid]=PCCsPerLayerBX[(tree.run, tree.LS)][Layer][bxid]/float(tree.BXNo[bxid])    

        PCCsPerLS[(tree.run,tree.LS)][0].append([PCCsPerEntry[(tree.run,tree.LS)][0],1])
        for layer in range(1,6):
            PCCsPerLS[(tree.run,tree.LS)][layer].append([PCCsPerEntry[(tree.run,tree.LS)][layer],1])
        for bxid in bxids:
            if not PCCsPerLS[(tree.run,tree.LS)][10].has_key(bxid):
                PCCsPerLS[(tree.run,tree.LS)][10][bxid]=[]
            PCCsPerLS[(tree.run,tree.LS)][10][bxid].append([PCCsPerEntry[(tree.run,tree.LS)][10][bxid],1])
            for Layer in range(5):
                if not PCCsPerLayerBXPerLS[(tree.run, tree.LS)][Layer].has_key(bxid):
                    PCCsPerLayerBXPerLS[(tree.run, tree.LS)][Layer][bxid]=[]
                PCCsPerLayerBXPerLS[(tree.run, tree.LS)][Layer][bxid].append([PCCsPerLayerBX[(tree.run, tree.LS)][Layer][bxid], 1])


cmskeys=PCCsPerLS.keys()
brilkeys=onlineLumi.keys()
if "runInfo" in brilkeys:
    brilkeys.remove("runInfo")


LSKeys=list(set(cmskeys+brilkeys))
# if batch only look at keys in both
if args.isBatch:
    #Always store PCC data even when there is no corresponding BRIL data
    LSKeys=cmskeys
    #if args.nobril or args.beamonly:
    #    LSKeys=cmskeys
    #else:
    #    LSKeys=list(set(cmskeys).intersection(brilkeys))
    
LSKeys.sort()

print LSKeys
newfilename="dataCertification_"+str(LSKeys[0][0])+"_"+str(LSKeys[-1][0])+"_"+args.label+".root"
if args.outPath!="":
    newfilename=outpath+"/"+newfilename
newfile=ROOT.TFile.Open(newfilename,"RECREATE")
newtree=ROOT.TTree("certtree","validationtree")

fill= array.array( 'I', [ 0 ] )
run = array.array( 'I', [ 0 ] )
LS  = array.array( 'I', [ 0 ] )
timeStamp = array.array( 'i', [ 0 ] )
nBX = array.array( 'I', [ 0 ] )
eventRate  = array.array( 'd', [ 0 ] )
nActiveBX = array.array( 'I', [ 0 ] )
nBXHFET = array.array( 'I', [ 0 ] )
nBXHFOC = array.array( 'I', [ 0 ] )
nBXBCMF = array.array( 'I', [ 0 ] )
nBXPLT = array.array( 'I', [ 0 ] )

nCluster    = array.array( 'd', [ 0 ] )
nClusterError    = array.array( 'd', [ 0 ] )
nPCPerLayer = array.array( 'd', 5*[ 0 ] )
nTrigger = array.array('d', [ 0 ] )

HFETLumi    = array.array( 'd', [ 0 ] )
HFOCLumi    = array.array( 'd', [ 0 ] )
BCMFLumi  = array.array( 'd', [ 0 ] )
PLTLumi   = array.array( 'd', [ 0 ] )
BestLumi  = array.array( 'd', [ 0 ] )
BestLumi_PU  = array.array( 'd', [ 0 ] )
PC_PU  = array.array( 'd', [ 0 ] )

HFETLumi_perBX = array.array( 'd', 3600*[ -1 ] )
HFOCLumi_perBX = array.array( 'd', 3600*[ -1 ] )

BCMFLumi_perBX = array.array( 'd', 3600*[ -1 ] )
PLTLumi_perBX = array.array('d', 3600*[ -1 ] )

HFETBXid = array.array('I', 3600*[ 0 ] )
HFOCBXid = array.array('I', 3600*[ 0 ] )
BCMFBXid = array.array('I', 3600*[ 0 ] )
PLTBXid = array.array('I', 3600*[ 0 ] )

HFETLumi_integrated    = array.array( 'd', [ 0 ] )
HFOCLumi_integrated  = array.array( 'd', [0])
BCMFLumi_integrated  = array.array( 'd', [ 0 ] )
PLTLumi_integrated   = array.array( 'd', [ 0 ] )
BestLumi_integrated  = array.array( 'd', [ 0 ] )

hasBrilData = array.array('b', [0])
hasCMSData  = array.array('b', [0])

PC_lumi_B0      = array.array( 'd', [ 0 ] )
PC_lumi_B3p8    = array.array( 'd', [ 0 ] )
PC_lumi_integrated_B0      = array.array( 'd', [ 0 ] )
PC_lumi_integrated_B3p8    = array.array( 'd', [ 0 ] )
PC_lumi_integrated_error_B0      = array.array( 'd', [ 0 ] )
PC_lumi_integrated_error_B3p8    = array.array( 'd', [ 0 ] )

PC_lumi_B0_perBX  = array.array('d', 3600*[ 0 ])
PC_lumi_B3p8_perBX = array.array('d', 3600*[ 0 ])
PC_lumi_B3p8_BP_perBX = array.array('d', 3600*[ 0 ])
PC_lumi_B3p8_FP_perBX = array.array('d', 3600*[ 0 ])
PC_lumi_B3p8_layer0_perBX = array.array('d', 3600*[ 0 ])
PC_lumi_B3p8_layer1_perBX = array.array('d', 3600*[ 0 ])
PC_lumi_B3p8_layer2_perBX = array.array('d', 3600*[ 0 ])
PC_lumi_B3p8_layer3_perBX = array.array('d', 3600*[ 0 ])
PC_lumi_B3p8_layer4_perBX = array.array('d', 3600*[ 0 ])

PC_xsec         = array.array( 'd', [ 0 ] )
PC_xsec_layers  = array.array( 'd', 5*[ 0 ] )

nPCPerBXid  = array.array( 'd', 3600*[ 0 ] )
PCBXid        = array.array( 'I', 3600*[ 0 ] )


goodVertices  = array.array( 'd', [ 0 ] )
goodVertices_Lumi = array.array('d', [ 0 ] )
goodVertices_xsec  = array.array( 'd', [ 0 ] )
goodVertices_eff  = array.array( 'd', [ 0 ] )


goodVertices_perBX  = array.array( 'd', 3600*[ 0 ] )
goodVertices_Lumi_perBX = array.array( 'd', 3600*[ 0 ] )
goodVertices_perBX_xsec  = array.array( 'd', 3600*[ 0 ] )
goodVertices_perBX_eff  = array.array( 'd', 3600*[ 0 ] )


tightVertices  = array.array( 'd', [ 0 ] )
tightVertices_Lumi = array.array('d', [ 0 ] )
tightVertices_xsec  = array.array( 'd', [ 0 ] )
tightVertices_eff  = array.array( 'd', [ 0 ] )


tightVertices_perBX  = array.array( 'd', 3600*[ 0 ] )
tightVertices_Lumi_perBX = array.array( 'd', 3600*[ 0 ] )
tightVertices_perBX_xsec  = array.array( 'd', 3600*[ 0 ] )
tightVertices_perBX_eff  = array.array( 'd', 3600*[ 0 ] )


validVertices  = array.array( 'd', [ 0 ] )
validVertices_Lumi = array.array( 'd', [ 0 ] )
validVertices_xsec  = array.array( 'd', [ 0 ] )
validVertices_eff  = array.array( 'd', [ 0 ] )

validVertices_perBX  = array.array( 'd', 3600*[ 0 ] )
validVertices_Lumi_perBX = array.array( 'd', 3600*[ 0 ] )
validVertices_perBX_xsec  = array.array( 'd', 3600*[ 0 ] )
validVertices_perBX_eff  = array.array( 'd', 3600*[ 0 ] )



newtree.Branch("fill",fill,"fill/I")
newtree.Branch("run",run,"run/I")
newtree.Branch("LS",LS,"LS/I")
newtree.Branch("timeStamp", timeStamp, "timeStamp/i")
newtree.Branch("eventRate",eventRate,"eventRate/D")
newtree.Branch("nActiveBX",nActiveBX,"nActiveBX/I")
newtree.Branch("nBX",nBX,"nBX/I")
newtree.Branch("nBXHFET", nBXHFET, "nBXHFET/I")
newtree.Branch("nBXHFOC", nBXHFOC, "nBXHFOC/I")
newtree.Branch("nBXBCMF", nBXBCMF, "nBXBCMF/I")
newtree.Branch("nBXPLT", nBXPLT, "nBXPLT/I")

newtree.Branch("nCluster",nCluster,"nCluster/D")
newtree.Branch("nClusterError",nClusterError,"nClusterError/D")
newtree.Branch("nPCPerLayer",nPCPerLayer,"nPCPerLayer[5]/D")

newtree.Branch("PC_lumi_B0",PC_lumi_B0,"PC_lumi_B0/D")
newtree.Branch("PC_lumi_B3p8",PC_lumi_B3p8,"PC_lumi_B3p8/D")
newtree.Branch("PC_lumi_integrated_B0",PC_lumi_integrated_B0,"PC_lumi_integrated_B0/D")
newtree.Branch("PC_lumi_integrated_B3p8",PC_lumi_integrated_B3p8,"PC_lumi_integrated_B3p8/D")
newtree.Branch("PC_lumi_integrated_error_B0",PC_lumi_integrated_error_B0,"PC_lumi_integrated_error_B0/D")
newtree.Branch("PC_lumi_integrated_error_B3p8",PC_lumi_integrated_error_B3p8,"PC_lumi_integrated_error_B3p8/D")

newtree.Branch("PC_lumi_B0_perBX", PC_lumi_B0_perBX, "PC_lumi_B0_perBX[nBX]/D")
newtree.Branch("PC_lumi_B3p8_perBX", PC_lumi_B3p8_perBX, "PC_lumi_B3p8_perBX[nBX]/D")

newtree.Branch("PC_lumi_B3p8_BP_perBX", PC_lumi_B3p8_BP_perBX, "PC_lumi_B3p8_BP_perBX[nBX]/D")
newtree.Branch("PC_lumi_B3p8_FP_perBX", PC_lumi_B3p8_FP_perBX, "PC_lumi_B3p8_FP_perBX[nBX]/D")

newtree.Branch("PC_lumi_B3p8_layer0_perBX", PC_lumi_B3p8_layer0_perBX, "PC_lumi_B3p8_layer0_perBX[nBX]/D")
newtree.Branch("PC_lumi_B3p8_layer1_perBX", PC_lumi_B3p8_layer1_perBX, "PC_lumi_B3p8_layer1_perBX[nBX]/D")
newtree.Branch("PC_lumi_B3p8_layer2_perBX", PC_lumi_B3p8_layer2_perBX, "PC_lumi_B3p8_layer2_perBX[nBX]/D")
newtree.Branch("PC_lumi_B3p8_layer3_perBX", PC_lumi_B3p8_layer3_perBX, "PC_lumi_B3p8_layer3_perBX[nBX]/D")
newtree.Branch("PC_lumi_B3p8_layer4_perBX", PC_lumi_B3p8_layer4_perBX, "PC_lumi_B3p8_layer4_perBX[nBX]/D")


newtree.Branch("PC_xsec",PC_xsec,"PC_xsec/D")
newtree.Branch("PC_xsec_layers",PC_xsec_layers,"PC_xsec_layers[5]/D")

newtree.Branch("PCBXid",PCBXid,"PCBXid[nBX]/I")
newtree.Branch("nPCPerBXid",nPCPerBXid,"nPCPerBXid[nBX]/D")

newtree.Branch("BestLumi",BestLumi,"BestLumi/D")
newtree.Branch("HFETLumi",HFETLumi,"HFETLumi/D")
newtree.Branch("HFOCLumi",HFOCLumi,"HFOCLumi/D")
newtree.Branch("BCMFLumi",BCMFLumi,"BCMFLumi/D")
newtree.Branch("PLTLumi",PLTLumi,"PLTLumi/D")

newtree.Branch("HFETLumi_perBX", HFETLumi_perBX, "HFETLumi_perBX[nBXHFET]/D")
newtree.Branch("HFOCLumi_perBX", HFOCLumi_perBX, "HFOCLumi_perBX[nBXHFOC]/D")
newtree.Branch("BCMFLumi_perBX", BCMFLumi_perBX, "BCMFLumi_perBX[nBXBCMF]/D")
newtree.Branch("PLTLumi_perBX", PLTLumi_perBX, "PLTLumi_perBX[nBXPLT]/D")

newtree.Branch("HFETBXid", HFETBXid, "HFETBXid[nBXHFET]/I")
newtree.Branch("HFOCBXid", HFOCBXid, "HFOCBXid[nBXHFOC]/I")
newtree.Branch("BCMFBXid", BCMFBXid, "BCMFBXid[nBXBCMF]/I")
newtree.Branch("PLTBXid", PLTBXid, "PLTBXid[nBXPLT]/I")

newtree.Branch("BestLumi_integrated",BestLumi_integrated,"BestLumi_integrated/D")
newtree.Branch("HFETLumi_integrated",HFETLumi_integrated,"HFETLumi_integrated/D")
newtree.Branch("HFOCLumi_integrated",HFOCLumi_integrated,"HFOCLumi_integrated/D")
newtree.Branch("BCMFLumi_integrated",BCMFLumi_integrated,"BCMFLumi_integrated/D")
newtree.Branch("PLTLumi_integrated",PLTLumi_integrated,"PLTLumi_integrated/D")

newtree.Branch("BestLumi_PU",BestLumi_PU,"BestLumi_PU/D")
newtree.Branch("PC_PU",PC_PU,"PC_PU/D")

newtree.Branch("hasBrilData",hasBrilData,"hasBrilData/O")
newtree.Branch("hasCMSData",hasCMSData,"hasCMSData/O")

newtree.Branch("goodVertices",      goodVertices,     "goodVertices/D")
newtree.Branch("goodVertices_Lumi", goodVertices_Lumi,    "goodVertices/D")
newtree.Branch("goodVertices_xsec", goodVertices_xsec,"goodVertices_xsec/D")
newtree.Branch("goodVertices_eff",  goodVertices_eff, "goodVertices_eff/D")
newtree.Branch("goodVertices_perBX",      goodVertices_perBX,     "goodVertices_perBX[nBX]/D")
newtree.Branch("goodVertices_Lumi_perBX", goodVertices_Lumi_perBX, "goodVertices_Lumi_perBX[nBX]/D")
newtree.Branch("goodVertices_perBX_xsec", goodVertices_perBX_xsec,"goodVertices_perBX_xsec[nBX]/D")
newtree.Branch("goodVertices_perBX_eff",  goodVertices_perBX_eff, "goodVertices_perBX_eff[nBX]/D")

newtree.Branch("tightVertices",      tightVertices,     "tightVertices/D")
newtree.Branch("tightVertices_Lumi", tightVertices_Lumi,    "tightVertices/D")
newtree.Branch("tightVertices_xsec", tightVertices_xsec,"tightVertices_xsec/D")
newtree.Branch("tightVertices_eff",  tightVertices_eff, "tightVertices_eff/D")
newtree.Branch("tightVertices_perBX",      tightVertices_perBX,     "tightVertices_perBX[nBX]/D")
newtree.Branch("tightVertices_Lumi_perBX", tightVertices_Lumi_perBX, "tightVertices_Lumi_perBX[nBX]/D")
newtree.Branch("tightVertices_perBX_xsec", tightVertices_perBX_xsec,"tightVertices_perBX_xsec[nBX]/D")
newtree.Branch("tightVertices_perBX_eff",  tightVertices_perBX_eff, "tightVertices_perBX_eff[nBX]/D")

newtree.Branch("validVertices",      validVertices,     "validVertices/D")
newtree.Branch("validVertices_Lumi", validVertices_Lumi, "validVertices_Lumi/D")
newtree.Branch("validVertices_xsec", validVertices_xsec,"validVertices_xsec/D")
newtree.Branch("validVertices_eff",  validVertices_eff, "validVertices_eff/D")
newtree.Branch("validVertices_perBX",      validVertices_perBX,     "validVertices_perBX[nBX]/D")
newtree.Branch("validVertices_Lumi_perBX", validVertices_Lumi_perBX, "validVertices_Lumi_perBX[nBX]/D")
newtree.Branch("validVertices_perBX_xsec", validVertices_perBX_xsec,"validVertices_perBX_xsec[nBX]/D")
newtree.Branch("validVertices_perBX_eff",  validVertices_perBX_eff, "validVertices_perBX_eff[nBX]/D")


PC_calib_xsec={}
PC_calib_xsec["B0_pp13TeV"]=9.0e6
PC_calib_xsec["B3p8_pp13TeV"]=9.0e6
# scale with PLT 3.51E-28/4.95E-28*9.4
PC_calib_xsec["B0_pp5TeV"]=6.45e6
PC_calib_xsec["B3p8_pp5TeV"]=6.45e6

hists={}
PCCPerLayer=[118.,44.3,39.2,34.9,22.3,23.9] #from MC

for key in LSKeys:
#for key in cmskeys:
    #print key
    run[0]=key[0]
    LS[0]=key[1]

    takenHF=False
    if runInfo.has_key("nActiveBXHF"):
        try:
            if runInfo["nActiveBXHF"].has_key(run[0]):
                if int(runInfo["nActiveBXHF"][run[0]])>0:
                    nActiveBX[0]=int(runInfo["nActiveBXHF"][run[0]])
                    takenHF=True
        except:
            takenHF=False
    if runInfo.has_key("nActiveBXBEAMINFO") and not takenHF:
        if runInfo["nActiveBXBEAMINFO"].has_key(run[0]):
            nActiveBX[0]=int(runInfo["nActiveBXBEAMINFO"][run[0]])
        else:
            print "no",run[0],"among keys"

    hasBrilData[0]=False
    hasCMSData[0]=False
    
    HFETLumi[0]=-1
    HFOCLumi[0]=-1
    BestLumi[0]=-1
    PLTLumi[0] =-1
    BCMFLumi[0]=-1
    
    HFETLumi_integrated[0]=-1
    HFOCLumi_integrated[0]=-1
    BestLumi_integrated[0]=-1
    PLTLumi_integrated[0] =-1
    BCMFLumi_integrated[0]=-1
        
    BestLumi_PU[0]=-1
    PC_PU[0]=-1
    PC_xsec[0]=-1

    PC_lumi_B0[0]=-1
    PC_lumi_B3p8[0]=-1
    PC_lumi_integrated_B0[0]=-1
    PC_lumi_integrated_B3p8[0]=-1
    PC_lumi_integrated_error_B0[0]=-1
    PC_lumi_integrated_error_B3p8[0]=-1

    goodVertices[0]=-1
    goodVertices_xsec[0]=-1
    goodVertices_eff[0]=-1

    validVertices[0]=-1
    validVertices_xsec[0]=-1
    validVertices_eff[0]=-1

    for layer in range(0,5):
        PC_xsec_layers[layer]=-1
        nPCPerLayer[layer]=-1

    if key in brilkeys:
        try:
            hasBrilData[0]=True
            fill[0]=int(onlineLumi[key]['fill'])
            if onlineLumi[key].has_key('best'):
                BestLumi_integrated[0]=float(onlineLumi[key][onlineLumi[key]['best']])
                BestLumi[0]=BestLumi_integrated[0]
            else:
                BestLumi_integrated[0]=float(onlineLumi[key]['HFOC'])
                BestLumi[0]=BestLumi_integrated[0]
            if onlineLumi[key].has_key('PU_best'):
                BestLumi_PU[0]=float(onlineLumi[key]['PU_best'])
                
            if BestLumi[0]>0:
                BestLumi[0]=BestLumi[0]/t_LS
            if onlineLumi[key].has_key('HFET'):
                HFETLumi_integrated[0]=float(onlineLumi[key]['HFET'])
                HFETLumi[0]=HFETLumi_integrated[0]
                if HFETLumi[0]>0:
                    HFETLumi[0]=HFETLumi[0]/t_LS
            if onlineLumi[key].has_key('HFOC'):
                HFOCLumi_integrated[0]=float(onlineLumi[key]['HFOC'])
                HFOCLumi[0]=HFOCLumi_integrated[0]
                if HFOCLumi[0]>0:
                    HFOCLumi[0]=HFOCLumi[0]/t_LS
            if onlineLumi[key].has_key('PLTZERO'):
                PLTLumi_integrated[0]=float(onlineLumi[key]['PLTZERO'])
                PLTLumi[0]=PLTLumi_integrated[0]
                if PLTLumi[0]>0:
                    PLTLumi[0]=PLTLumi[0]/t_LS
            if onlineLumi[key].has_key('BCM1F'):
                BCMFLumi_integrated[0]=float(onlineLumi[key]['BCM1F'])
                BCMFLumi[0]=BCMFLumi_integrated[0]
                if BCMFLumi[0]>0:
                    BCMFLumi[0]=BCMFLumi[0]/t_LS

            if onlineLumi[key].has_key('HFOC_BX'):
                isNan=False
                nBXHFOC[0] = len(onlineLumi[key]['HFOC_BX'])
                idxHFOC=0
                HFOCbxkeys = onlineLumi[key]['HFOC_BX'].keys()
                HFOCbxkeys.sort()
                #print "HF length", len(HFbxkeys)
                for HFOCbxkey in HFOCbxkeys :
                    HFOCBXid[idxHFOC] = int(HFOCbxkey)
                    if math.isnan(onlineLumi[key]['HFOC_BX'][HFOCbxkey]):
                        isNan=True
                    HFOCLumi_perBX[idxHFOC] = float(onlineLumi[key]['HFOC_BX'][HFOCbxkey])/t_LS
                    idxHFOC = idxHFOC+1
                if isNan:
                    print key, "This LS has 'nan' value"
                    continue

            if onlineLumi[key].has_key('HFET_BX'):
                isNan=False
                nBXHFET[0] = len(onlineLumi[key]['HFET_BX'])
                idxHFET=0
                HFETbxkeys = onlineLumi[key]['HFET_BX'].keys()
                HFETbxkeys.sort()
                #print "HF length", len(HFbxkeys)
                for HFETbxkey in HFETbxkeys :
                    HFETBXid[idxHFET] = int(HFETbxkey)
                    if math.isnan(onlineLumi[key]['HFET_BX'][HFETbxkey]):
                        isNan=True
                    HFETLumi_perBX[idxHFET] = float(onlineLumi[key]['HFET_BX'][HFETbxkey])/t_LS
                    idxHFET = idxHFET+1
                if isNan:
                    print key, "This LS has 'nan' value"
                    continue


            if onlineLumi[key].has_key('PLTZERO_BX'):
                nBXPLT[0] = len(onlineLumi[key]['PLTZERO_BX'])
                idxPLT=0
                PLTbxkeys = onlineLumi[key]['PLTZERO_BX'].keys()
                PLTbxkeys.sort()
                #print PLTbxkeys
                for PLTbxkey in PLTbxkeys :
                    PLTBXid[idxPLT] = int(PLTbxkey)
                    PLTLumi_perBX[idxPLT] = float(onlineLumi[key]['PLTZERO_BX'][PLTbxkey])/t_LS
                    idxPLT = idxPLT+1
        
            if onlineLumi[key].has_key('BCM1F_BX'):
                nBXBCMF[0] = len(onlineLumi[key]['BCM1F_BX'])
                idxBCMF=0
                BCMFbxkeys = onlineLumi[key]['BCM1F_BX'].keys()
                BCMFbxkeys.sort()
                #print len(BCMFbxkeys)
                for BCMFbxkey in BCMFbxkeys :
                    BCMFBXid[idxBCMF] = int(BCMFbxkey)
                    BCMFLumi_perBX[idxBCMF] = float(onlineLumi[key]['BCM1F_BX'][BCMFbxkey])/t_LS
                    idxBCMF = idxBCMF+1
               
                
        except:
            print "Failed in brilkey",key#,onlineLumi[key]

    if key in cmskeys:
        try:
            hasCMSData[0]=True
            nBX[0]=nBXs[key]
            eventRate[0]=eventRates[key]
            timeStamp[0]=timeStamps[key]
            
            count=0
            if args.includeVertices:
                goodVertices[0]=AverageWithWeight(goodVertexCounts[key][0])
                tightVertices[0]=AverageWithWeight(tightVertexCounts[key][0])
                validVertices[0]=AverageWithWeight(validVertexCounts[key][0])
                bxids=goodVertexCounts[key][1].keys()
                bxids.sort()
                
                ibx=0
                for bxid in bxids:
                    goodVertices_perBX[ibx]=AverageWithWeight(goodVertexCounts[key][1][bxid])
                    tightVertices_perBX[ibx]=AverageWithWeight(tightVertexCounts[key][1][bxid])
                    validVertices_perBX[ibx]=AverageWithWeight(validVertexCounts[key][1][bxid])
                    ibx=ibx+1

            for PCCs in PCCsPerLS[key]:
                #print key,count
                if count==0:
                    mean,error=GetMeanAndMeanError(PCCs)
                    nCluster[0]=mean
                    nClusterError[0]=error
                elif count<10:
                    mean,error=GetMeanAndMeanError(PCCs)
                    nPCPerLayer[count-1]=mean
                else:
                    ibx=0
                    bxids=PCCs.keys()
                    bxids.sort()
                    #print PCCsPerLayerBXPerLS[key]
                    for bxid in bxids:
                        if bxid<0: 
                            continue
                        mean,error=GetMeanAndMeanError(PCCs[bxid])
                        PCBXid[ibx]=bxid
                        nPCPerBXid[ibx]=mean
                        totalPCperBX=mean*math.pow(2,18)
                        PC_lumi_B0_perBX[ibx]=totalPCperBX/PC_calib_xsec["B0_"+args.collisionType]/t_LS
                        PC_lumi_B3p8_perBX[ibx]=totalPCperBX/PC_calib_xsec["B3p8_"+args.collisionType]/t_LS
                        for Layer in range(5):
                            if not PCCsPerLayerBXPerLS[key][Layer].has_key(bxid):
                                continue
                            lmean,lerror=GetMeanAndMeanError(PCCsPerLayerBXPerLS[key][Layer][bxid])
                            #print "lmean,", lmean, "Layer", Layer 
                            if Layer==1 or Layer==2:
                                PC_lumi_B3p8_BP_perBX[ibx]=lmean*math.pow(2,18)/PC_calib_xsec["B3p8_"+args.collisionType]/t_LS
                            if Layer==3 or Layer==4:
                                PC_lumi_B3p8_FP_perBX[ibx]=lmean*math.pow(2,18)/PC_calib_xsec["B3p8_"+args.collisionType]/t_LS        
                            if Layer==0:
                                PC_lumi_B3p8_layer0_perBX[ibx]=lmean*math.pow(2,18)/PC_calib_xsec["B3p8_"+args.collisionType]/t_LS
                            if Layer==1:
                                PC_lumi_B3p8_layer1_perBX[ibx]=lmean*math.pow(2,18)/PC_calib_xsec["B3p8_"+args.collisionType]/t_LS
                            if Layer==2:
                                PC_lumi_B3p8_layer2_perBX[ibx]=lmean*math.pow(2,18)/PC_calib_xsec["B3p8_"+args.collisionType]/t_LS
                            if Layer==3:
                                PC_lumi_B3p8_layer3_perBX[ibx]=lmean*math.pow(2,18)/PC_calib_xsec["B3p8_"+args.collisionType]/t_LS
                            if Layer==4:
                                PC_lumi_B3p8_layer4_perBX[ibx]=lmean*math.pow(2,18)/PC_calib_xsec["B3p8_"+args.collisionType]/t_LS
 
                        ibx=ibx+1
                        if ibx>nBX[0]:
                            print "ibx,nBX[0],",ibx,nBX[0],", but WHY?!!!"

                count=count+1 
            totalPC=nCluster[0]*math.pow(2,18)*nActiveBX[0]
            totalPCError=nClusterError[0]*math.pow(2,18)*nActiveBX[0]
            
            PC_lumi_B0[0]=totalPC/PC_calib_xsec["B0_"+args.collisionType]/t_LS
            PC_lumi_B3p8[0]=totalPC/PC_calib_xsec["B3p8_"+args.collisionType]/t_LS
            PC_lumi_integrated_B0[0]=totalPC/PC_calib_xsec["B0_"+args.collisionType]
            PC_lumi_integrated_B3p8[0]=totalPC/PC_calib_xsec["B3p8_"+args.collisionType]
            PC_lumi_integrated_error_B0[0]=totalPCError/PC_calib_xsec["B0_"+args.collisionType]
            PC_lumi_integrated_error_B3p8[0]=totalPCError/PC_calib_xsec["B3p8_"+args.collisionType]
            
        except:
            print "Failed in cmskey",key
            
    if hasCMSData[0] and hasBrilData[0]: 
        try:
            totalOrbitsPerLS=math.pow(2,18)*nActiveBX[0]
            PC_xsec[0]=nCluster[0]/BestLumi_integrated[0]*totalOrbitsPerLS
            if args.includeVertices:
                goodVertices_Lumi[0]=goodVertices[0]*totalOrbitsPerLS/(1e6)
                goodVertices_xsec[0]=goodVertices[0]/BestLumi_integrated[0]*totalOrbitsPerLS
                goodVertices_eff[0]=goodVertices_xsec[0]/xsec_ub
                tightVertices_Lumi[0]=tightVertices[0]*totalOrbitsPerLS/(1e6)
                tightVertices_xsec[0]=tightVertices[0]/BestLumi_integrated[0]*totalOrbitsPerLS
                tightVertices_eff[0]=tightVertices_xsec[0]/xsec_ub
                validVertices_Lumi[0]=validVertices[0]*totalOrbitsPerLS
                validVertices_xsec[0]=validVertices[0]/BestLumi_integrated[0]*totalOrbitsPerLS
                validVertices_eff[0]=validVertices_xsec[0]/xsec_ub
                ibx=0
                for bxid in bxids:
                    # FIXME I should really use the lumi for this bx and not multiply by number of bxs
                    goodVertices_Lumi_perBX[ibx]=goodVertices_Lumi_perBX[ibx]*totalOrbitsPerLS/(1e6)
                    goodVertices_perBX_xsec[ibx]=goodVertices_perBX[ibx]/BestLumi_integrated[0]*math.pow(2,18)*nActiveBX[0]
                    goodVertices_perBX_eff[ibx]=goodVertices_perBX_xsec[ibx]/xsec_ub
                    tightVertices_Lumi_perBX[ibx]=tightVertices_Lumi_perBX[ibx]*totalOrbitsPerLS/(1e6)
                    tightVertices_perBX_xsec[ibx]=tightVertices_perBX[ibx]/BestLumi_integrated[0]*math.pow(2,18)*nActiveBX[0]
                    tightVertices_perBX_eff[ibx]=tightVertices_perBX_xsec[ibx]/xsec_ub
                    validVertices_Lumi_perBX[ibx]=validVertices_perBX[ibx]*totalOrbitsPerLS
                    validVertices_perBX_xsec[ibx]=validVertices_perBX[ibx]/BestLumi_integrated[0]*math.pow(2,18)*nActiveBX[0]
                    validVertices_perBX_eff[ibx]=validVertices_perBX_xsec[ibx]/xsec_ub
                    ibx=ibx+1
            
            for layer in range(0,5):
                PC_xsec_layers[layer]=nPCPerLayer[layer]/BestLumi_integrated[0]*totalOrbitsPerLS
            if BestLumi_PU[0]==0 and BestLumi[0]>0 and nActiveBX[0]>0:
                BestLumi_PU[0]=BestLumi[0]*xsec_ub/nActiveBX[0]/f_LHC
            
            if PC_lumi_B3p8[0]>0 and nActiveBX[0]>0:
                PC_PU[0]=PC_lumi_B3p8[0]*xsec_ub/nActiveBX[0]/f_LHC
                
        except:
            print "Failed cms+bril computation",key,onlineLumi[key]

    newtree.Fill()

newfile.Write()
newfile.Close()

