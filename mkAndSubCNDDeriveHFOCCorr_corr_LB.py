import ROOT
import sys
import argparse
import os
import subprocess
import json
import glob
from shutil import copyfile


parser=argparse.ArgumentParser()
parser.add_argument("-p",  "--path",  help="EOS path to PCCNTuples... /store/user/..")
parser.add_argument("--para",  default="0.074,0.0,0.00086,0.014",  help="Parameters for afterglow corrections (default:  0.074,0.0,0.00086,0.014)")
parser.add_argument("--quad", default=0.00,  help="Quadratic correction to trains (default:  0)")
parser.add_argument("-d", "--jobdir", default="JobsDir", help="Output directory")
parser.add_argument("-s", "--sub", action='store_true', default=False, help="bsub created jobs")
parser.add_argument("-q", "--queue", type=str, default="8nh", help="lxbatch queue (default:  8nh)")
parser.add_argument("-c", "--checkOutput", action='store_true', default=False, help="check if the output file exists")
#parser.add_argument('-r', '--run', default="", help="Comma separted list of runs")
parser.add_argument("-a", "--all", action='store_true', default=False, help="store all the data to a single histogram")
parser.add_argument('-l', '--label', default="", help="Label in output file")
parser.add_argument('--nLSInLumiBlock', default=50, help="Number of LSs to group for evaluation (Default:  500)")
parser.add_argument('--buildFromScratch', default=1, type=int, help="Start from cert trees (default); do --buildFromScratch 0 to start from \"Before\" histograms")
parser.add_argument('--bunchtrain', default=False, action="store_true", help="apply the bunch train correction")
args=parser.parse_args()

#Fill   Bfield    Runs 


#jobid is the run
def MakeJob(outputdir,jobid, pathname):
    curr=os.getcwd()
    joblines=[]
    joblines.append("#!/bin/bash")
    joblines.append("source /cvmfs/cms.cern.ch/cmsset_default.sh")
    joblines.append("cd "+outputdir)
    joblines.append("cmsenv")
    # if args.buildFromScratch==0:
    makeDataCMD="python DeriveHFOCCorrections_corr_LB.py -f "+args.path+"/"+pathname
    if args.bunchtrain:
        makeDataCMD = makeDataCMD+" --bunchtrain "
    #elif args.buildFromScratch==1:
    # makeDataCMD="python ../DerivePCCCorrections_byFill_LB.py -f ../"+args.path+"/"+filename
    makeDataCMD=makeDataCMD+" -b --auto "
    
    thisLabel=args.label

    forLabel="_fills_"+str(jobid)
    thisLabel=thisLabel+forLabel
    

    #makeDataCMD=makeDataCMD+" -p "+args.para
    #forLabel="_paras_"+args.para.replace(",","_")
    #forLabel=forLabel.replace(".","p")
    #thisLabel=thisLabel+forLabel
    
    makeDataCMD=makeDataCMD+" --nLSInLumiBlock="+str(args.nLSInLumiBlock)
    #forLabel="_nLSInLumiBlock_"+str(args.nLSInLumiBlock)
    #thisLabel=thisLabel+forLabel

    #makeDataCMD=makeDataCMD+" --buildFromScratch="+str(args.buildFromScratch)
    #thisLabel=thisLabel+"_buildFromScratch"+str(args.buildFromScratch)
    
    makeDataCMD=makeDataCMD+" -l "+thisLabel
    if args.all:
        makeDataCMD=makeDataCMD+" -a "
    #makeDataCMD=makeDataCMD+" -r "+str(jobid)
        
    #print makeDataCMD
    joblines.append(makeDataCMD)
    
    scriptFile=open(outputdir+"/job_"+str(jobid)+".sh","w+")
    for line in joblines:
        scriptFile.write(line+"\n")
        
    scriptFile.close()

    cndlines = []
    cndlines.append("executable              = job_"+str(jobid)+".sh")
    cndlines.append("universe                = vanilla")
    cndlines.append("output                  = test_"+str(jobid)+".out")
    cndlines.append("error                   = test_"+str(jobid)+".err")
    cndlines.append("log                     = test_"+str(jobid)+".log")
    cndlines.append("transfer_input_files    = DeriveHFOCCorrections_corr_LB.py")
    cndlines.append("should_transfer_files   = YES")
    cndlines.append("when_to_transfer_output = ON_EXIT")
    cndlines.append("queue")
    cndFile = open(outputdir+"/condor_"+str(jobid), "w+")
    for line in cndlines:
        cndFile.write(line+"\n")
    cndFile.close()


def SubmitJob(job,queue="8nh"):
    baseName=str(job.split(".")[0])
    cmd="bsub -q "+queue+" -J "+baseName+" -o "+baseName+".log < "+str(job)
    output=os.system(cmd)
    if output!=0:
        print job,"did not submit properly"
        print cmd


# ls the eos directory
fileinfos=subprocess.check_output(["ls", args.path])
fileinfos=fileinfos.split("\n")
#if args.path.find("/store")==0:
#    fileinfos=subprocess.check_output(["/afs/cern.ch/project/eos/installation/0.3.15/bin/eos.select","ls", args.path])
#    fileinfos=fileinfos.split("\n")
#else:
#    fileinfos=subprocess.check_output(["ls", args.path])
#    fileinfos=fileinfos.split("\n")

#fileinfos=glob.glob("/afs/cern.ch/work/j/jingyu/CMSSW_8_0_5/src/tmp/cms"+args.path)
#filename = os.getcwd()+"/"+args.path
#print filename
#fileinfos= fileinfos.split("\n")

filenames={}
jobid=0
for fileinfo in fileinfos:
    filename=fileinfo

    print filename
    if filename.find(".root") == -1:
        continue

    print filename
    #if args.buildFromScratch==0:
    #    jobid=filename.split("/")[-1].split(".")[0].split("_")[4]
    #elif args.buildFromScratch==1:
    #    jobid=filename.split(".")[0].split("_")[2]
    jobid=filename.split(".")[0].split("_")[3]
    filenames[jobid]=filename
    #else:
    #    print "what are you doing?"
    #    sys.exit(-1)
    #print jobid, filename

#runsFromFileNames=[]

#for jobid in filenames:
#    #print filenames[jobid]
#    # FIXME change algo to open/close every file 
#    # and explicitly check for runs' presence.
#    parts=filenames[jobid].split("_")
#    #if parts[-2] not in runsFromFileNames:
#    #    runsFromFileNames.append(parts[-2])
#    #if parts[-3] not in runsFromFileNames:
#    #    runsFromFileNames.append(parts[-3])
#    if args.buildFromScratch==0:
#        if parts[4] not in runsFromFileNames:
#            runsFromFileNames.append(parts[4])
#    elif args.buildFromScratch==1:
#        if parts[2] not in runsFromFileNames:
#            runsFromFileNames.append(parts[2])

fullOutPath=os.getcwd()
if not os.path.exists(args.jobdir):
    os.makedirs(args.jobdir)
copyfile("DeriveHFOCCorrections_corr_LB.py", args.jobdir+"/DeriveHFOCCorrections_corr_LB.py")
fullOutPath=fullOutPath+"/"+args.jobdir
#idxs=[4410,4402,4398,4397,4393,4391,4386,4384,4381,4376]#[4364,4363,4360,4356,4349,4342,4341,4337,4332,4323,4322,4269,4268,4266,4257,4256,4254,4249,4246,4243,4231,4225,4224,4220,4219,4214,4212,4211,4210,4208,4207,4205,4201,4020,4019,4008,4006,4001]

ids = filenames.keys()
for idx in ids:
    MakeJob(fullOutPath,idx, filenames[idx])

if args.checkOutput:
    filesPresent=subprocess.check_output(["ls", args.jobdir])
    print filesPresent

if args.sub:
    print "Submitting",len(ids),"jobs (one per run found)"
    os.chdir(args.jobdir)
    for idx in ids:
        if args.checkOutput:
            if filesPresent.find("_"+str(idx)+".root")!=-1:
                print "Found file output for job",str(idx),"skipping"
                continue
        os.system("condor_submit condor_"+str(idx))
        #SubmitJob(args.jobdir+"/job_"+str(idx)+".sh",args.queue)
        #raw_input()
