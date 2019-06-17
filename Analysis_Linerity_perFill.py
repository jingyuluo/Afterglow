import sys, os
import argparse
import math
from math import fabs

sys.path.append('/Users/jingyuluo/Downloads/root_dir/lib')
import ROOT
from ROOT import TFile, TCanvas, TH1F
from ROOT import gStyle

gStyle.SetOptFit(1)


def find_fit_range(graph):
    x_list=[]
    nps = graph.GetN()
    for ip in range(nps):
        x_list.append(graph.GetX()[ip])

    x_list.sort()
    counts={}
    for ix in x_list:
        if not counts.has_key(int(ix/1.0)):
            counts[int(ix/1.0)]=1
        else:
            counts[int(ix/1.0)]+=1

    min_key = 40000
    max_key = -1

    #print counts
    for key in counts.keys():
        if counts[key]>1:
            if key<min_key:
                min_key=key
                
            if key>max_key:
                max_key=key
    #print min_key, max_key
    return 1.0*min_key, 1.0*(max_key+1)

def remove_outlier(graph):
    mean = graph.GetMean(2)
    np = graph.GetN()
    ip=0
    while ip<np:
        if fabs(graph.GetY()[ip]-mean)>mean*0.20:
            graph.RemovePoint(ip)
            ip-=1
            np-=1
        ip+=1


parser = argparse.ArgumentParser()

parser.add_argument("-f", "--file", help="The ROOT file for data")
parser.add_argument("-l", "--label", help="The label of the output file")


args = parser.parse_args()

filename = args.file

tfile = ROOT.TFile(filename)

ttree = tfile.Get("newtree")
outfile = ROOT.TFile("test_output_"+args.label+".root", "RECREATE")
csvfile = open("Fill_p0_p1_"+args.label+".csv", "w")

can = ROOT.TCanvas("can", "", 1000, 700)
can.SetTickx()
can.SetTicky()
can.cd()

Overall_Corr_Total = ROOT.TGraph()
Overall_Corr_Profile = ROOT.TProfile("total_pro", "total_pro", 100, 0, 7, "S")
nLB = ttree.GetEntries()
Type1Graphs_perFill = {}
NoiseGraphs_perFill = {}
iLB_perFill = {}

Overall_hist_Corrected = ROOT.TH1F("overall_hist", "overall_hist", 100, -0.02, 0.02)
Overall_hist_Corrected.Sumw2()

ttree.SetBranchStatus("*", 0)
ttree.SetBranchStatus("FILL", 1)

currfill = 0
for iLB in range(nLB):
    ttree.GetEntry(iLB)
    #print ttree.type1frac
    fill = ttree.FILL

    if fill != currfill:
        iLB_perFill[int(fill)]=0
        Type1Graphs_perFill[int(fill)]=ROOT.TGraphErrors()
        Type1Graphs_perFill[int(fill)].SetTitle("Overall Correction for Fill "+str(ttree.FILL)+"; Average SBIL (Hz/#mB); Correction Factor")
        NoiseGraphs_perFill[int(fill)]=ROOT.TGraphErrors()
        NoiseGraphs_perFill[int(fill)].SetTitle("Noise for Fill "+str(ttree.FILL)+"; Average SBIL (Hz/#mB); Noise")
        currfill = fill

ttree.SetBranchStatus("overallratio", 1)
ttree.SetBranchStatus("type1frac", 1)
ttree.SetBranchStatus("AveSBIL", 1)
ttree.SetBranchStatus("AveSBIL_corr", 1)
ttree.SetBranchStatus("noisefrac", 1)
ttree.SetBranchStatus("type1frac_err", 1)

eff_iLB=0
for iLB in range(nLB):
    ttree.GetEntry(iLB)
    fill = ttree.FILL
    Type1Graphs_perFill[int(fill)].SetPoint(iLB_perFill[int(fill)], ttree.AveSBIL, float(ttree.overallratio))
    Overall_Corr_Total.SetPoint(eff_iLB, ttree.AveSBIL, float(ttree.overallratio))
    Overall_Corr_Profile.Fill(ttree.AveSBIL, float(ttree.overallratio))
    Type1Graphs_perFill[int(fill)].SetPointError(iLB_perFill[int(fill)], 0, 0)
    NoiseGraphs_perFill[int(fill)].SetPoint(iLB_perFill[int(fill)], ttree.AveSBIL, ttree.AveSBIL*ttree.noisefrac/(1-ttree.noisefrac))
    iLB_perFill[int(fill)]+=1
    eff_iLB+=1

P0_vs_Fill = ROOT.TGraphErrors()
P1_vs_Fill = ROOT.TGraphErrors()
ifill = 0
fills = Type1Graphs_perFill.keys()
fills.sort()
for Fill in fills:
    can.Update()
    print Fill
    low_x,high_x = find_fit_range(Type1Graphs_perFill[Fill])
    print low_x, high_x
    remove_outlier(Type1Graphs_perFill[Fill])
    try:
        FitResult = Type1Graphs_perFill[Fill].Fit("pol1", "MF", "", low_x, high_x)
        FitResult = Type1Graphs_perFill[Fill].GetFunction("pol1")
    except:
        print "Problem with the Fill:", Fill
    Type1Graphs_perFill[Fill].SetMarkerStyle(23)
    Type1Graphs_perFill[Fill].SetMarkerSize(0.7)
    Type1Graphs_perFill[Fill].SetMarkerColor(ROOT.kBlue)
    Type1Graphs_perFill[Fill].GetYaxis().SetRangeUser(0.9,1.2)
    Type1Graphs_perFill[Fill].GetYaxis().SetTitleOffset(1.2)
    Type1Graphs_perFill[Fill].Draw("APE0Z")
    can.SaveAs("OverallCorrection_vs_SBIL_Fill"+str(Fill)+"_FitResult_"+args.label+".png")

    can.Update() 
    NoiseGraphs_perFill[Fill].SetMarkerStyle(23)
    NoiseGraphs_perFill[Fill].SetMarkerSize(0.7)
    NoiseGraphs_perFill[Fill].SetMarkerColor(ROOT.kBlue)
    NoiseGraphs_perFill[Fill].GetYaxis().SetRangeUser(-0.01,0.03)
    NoiseGraphs_perFill[Fill].GetYaxis().SetTitleOffset(1.2)
    NoiseGraphs_perFill[Fill].Draw("APE0Z")
    can.SaveAs("Noise_vs_SBIL_Fill"+str(Fill)+"_FitResult_"+args.label+".png")
    try:
        p0 = FitResult.GetParameter(0)
        p0err = FitResult.GetParError(0)
        p1 = FitResult.GetParameter(1)
        p1err = FitResult.GetParError(1)
        print "p0", p0
        csvfile.write(str(Fill)+","+str(p0)+","+str(p1)+"\n")
        P0_vs_Fill.SetPoint(ifill, float(Fill), p0)
        P0_vs_Fill.SetPointError(ifill, 0, p0err)
        P1_vs_Fill.SetPoint(ifill, float(Fill), p1)
        P1_vs_Fill.SetPointError(ifill, 0, p1err)
        outfile.WriteTObject(Type1Graphs_perFill[Fill], "type1vsSBIL_Fill"+str(Fill))
        outfile.WriteTObject(NoiseGraphs_perFill[Fill], "noisevsSBIL_Fill"+str(Fill))
        ifill+=1
    except:
        print "Problem with the Fill:", Fill

#print P0_vs_Fill.GetX()[0]
csvfile.close()
can.Update()
P0_vs_Fill.GetXaxis().SetTitle("Fill")
P0_vs_Fill.GetYaxis().SetTitle("p0")
P0_vs_Fill.GetYaxis().SetTitleOffset(1.2)
P0_vs_Fill.GetYaxis().SetRangeUser(0.5, 1.2)
P0_vs_Fill.SetMarkerStyle(23)
P0_vs_Fill.SetMarkerSize(0.7)
P0_vs_Fill.SetMarkerColor(ROOT.kBlue)
P0_vs_Fill.Draw("APE0Z")
can.SaveAs("P0_vs_Fill_"+args.label+".png")

can.Update()
P1_vs_Fill.GetXaxis().SetTitle("Fill")
P1_vs_Fill.GetYaxis().SetTitle("p1")
P1_vs_Fill.GetYaxis().SetTitleOffset(1.2)
P1_vs_Fill.GetYaxis().SetRangeUser(-0.05, 0.05)
P1_vs_Fill.SetMarkerStyle(23)
P1_vs_Fill.SetMarkerSize(0.7)
P1_vs_Fill.SetMarkerColor(ROOT.kBlue)
P1_vs_Fill.Draw("APE0Z")
can.SaveAs("P1_vs_Fill_"+args.label+".png")
outfile.WriteTObject(P0_vs_Fill, "p0_vs_fill")
outfile.WriteTObject(P1_vs_Fill, "p1_vs_fill")
outfile.WriteTObject(Overall_Corr_Total, "Overall_Corr_Total")
outfile.WriteTObject(Overall_Corr_Profile, "Overall_Corr_Profile")
outfile.WriteTObject(Overall_hist_Corrected, "Overall_hist_Corrected")

outfile.Close()
