import FWCore.ParameterSet.Config as cms

process = cms.Process("CSVTrainer")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.load("RecoBTau.JetTagComputer.jetTagRecord_cfi")
#process.load("RecoBTag.SecondaryVertex.combinedSecondaryVertexES_cfi")
#process.combinedSecondaryVertex.trackMultiplicityMin = cms.uint32(2)

# load the full reconstraction configuration, to make sure we're getting all needed dependencies
process.load("Configuration.StandardSequences.MagneticField_cff")
#process.load("Configuration.StandardSequences.Geometry_cff") #old one, to use for old releases
process.load("Configuration.Geometry.GeometryIdeal_cff") #new one
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load("Configuration.StandardSequences.Reconstruction_cff")

#process.GlobalTag.globaltag = cms.string("POSTLS170_V6::All")
process.GlobalTag.globaltag = cms.string("MCRUN2_75_V5")

from PhysicsTools.JetMCAlgos.AK4PFJetsMCPUJetID_cff import *
process.selectedAK4PFGenJets = ak4GenJetsMCPUJetID.clone()
process.matchedAK4PFGenJets = ak4PFJetsGenJetMatchMCPUJetID.clone()
process.matchedAK4PFGenJets.matched = cms.InputTag("selectedAK4PFGenJets")
process.matchedAK4PFGenJets.src = cms.InputTag("ak4PFJetsCHS")

#JTA for your jets
from RecoJets.JetAssociationProducers.j2tParametersVX_cfi import *
process.myak4JetTracksAssociatorAtVertex = cms.EDProducer("JetTracksAssociatorAtVertex",
                                                  j2tParametersVX,
                                                  jets = cms.InputTag("ak4PFJetsCHS")
                                                  )

#new input for impactParameterTagInfos
from RecoBTag.Configuration.RecoBTag_cff import *
process.impactParameterTagInfos.jetTracks = cms.InputTag("myak4JetTracksAssociatorAtVertex")



#select good primary vertex
from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
process.goodOfflinePrimaryVertices = cms.EDFilter(
    "PrimaryVertexObjectFilter",
    filterParams = pvSelector.clone( minNdof = cms.double(4.0), maxZ = cms.double(24.0) ),
    src=cms.InputTag('offlinePrimaryVertices')
    )

#input for softLeptonTagInfos
from RecoBTag.SoftLepton.softPFElectronTagInfos_cfi import *
process.softPFElectronsTagInfos.primaryVertex = cms.InputTag('goodOfflinePrimaryVertices')
process.softPFElectronsTagInfos.jets = cms.InputTag("ak4PFJetsCHS")
process.softPFElectronsTagInfos.useMCpromptElectronFilter = cms.bool(True)
from RecoBTag.SoftLepton.softPFMuonTagInfos_cfi import *
process.softPFMuonsTagInfos.primaryVertex = cms.InputTag('goodOfflinePrimaryVertices')
process.softPFMuonsTagInfos.jets = cms.InputTag("ak4PFJetsCHS")
process.softPFMuonsTagInfos.useMCpromptMuonFilter = cms.bool(True)

#process.combinedSecondaryVertexSoftLepton.trackMultiplicityMin = cms.uint32(2)


#for Inclusive Vertex Finder
process.load('RecoVertex/AdaptiveVertexFinder/inclusiveVertexing_cff')
process.load('RecoBTag/SecondaryVertex/inclusiveSecondaryVertexFinderTagInfos_cfi')
process.inclusiveVertexFinder.primaryVertices = cms.InputTag("goodOfflinePrimaryVertices")
process.trackVertexArbitrator.primaryVertices = cms.InputTag("goodOfflinePrimaryVertices")

# cut on decay length
process.inclusiveVertexFinder.vertexMinDLen2DSig = cms.double(1.25) #2.5 sigma for b tagger, default for C tagger was put on 0. However, lifetime D mesons on average about half of lifetime of B meson -> half of significance
process.inclusiveVertexFinder.vertexMinDLenSig = cms.double(0.25) #0.5 sigma for b tagger, default for C tagger was put on 0. However, lifetime D mesons on average about half of lifetime of B meson -> half of significance
#process.inclusiveVertexFinder.clusterizer.seedMin3DIPSignificance = cms.double(1.0) # default 1.2
#process.inclusiveVertexFinder.clusterizer.seedMin3DIPValue = cms.double(0.005) # default 0.005
#process.inclusiveVertexFinder.clusterScale = cms.double(0.5) # default 1. #I think it should be distanceRatio(10) now
process.inclusiveSecondaryVertexFinderTagInfos.vertexCuts.distSig2dMin = 1.5 # default value 3.0 to release cuts on flight dist, default for C tagger was put on 0. However, lifetime D mesons on average about half of lifetime of B meson -> half of distance


#for the flavour matching
from PhysicsTools.JetMCAlgos.HadronAndPartonSelector_cfi import selectedHadronsAndPartons
process.selectedHadronsAndPartons = selectedHadronsAndPartons.clone()

from PhysicsTools.JetMCAlgos.AK4PFJetsMCFlavourInfos_cfi import ak4JetFlavourInfos
process.jetFlavourInfosAK4PFJets = ak4JetFlavourInfos.clone()
process.jetFlavourInfosAK4PFJets.jets = cms.InputTag("ak4PFJetsCHS")

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(1)#000)
)


process.source = cms.Source("PoolSource",
	fileNames = cms.untracked.vstring(
      '/store/relval/CMSSW_7_5_0_pre5/RelValTTbar_13/GEN-SIM-RECO/MCRUN2_75_V5-v1/00000/383E39B7-BA0B-E511-A509-0025905B8582.root',
      '/store/relval/CMSSW_7_5_0_pre5/RelValTTbar_13/GEN-SIM-RECO/MCRUN2_75_V5-v1/00000/4AE0AEB0-BA0B-E511-86F9-002618943857.root',
      '/store/relval/CMSSW_7_5_0_pre5/RelValTTbar_13/GEN-SIM-RECO/MCRUN2_75_V5-v1/00000/F0BEEE9E-120B-E511-88DD-0025905A60C6.root'
	)
)


process.combinedSVMVATrainer = cms.EDAnalyzer("JetTagMVAExtractor",
	variables = cms.untracked.VPSet(
		cms.untracked.PSet( label = cms.untracked.string("CombinedSVRecoVertexNoSoftLepton"),  variables=cms.untracked.vstring(
"jetPt","jetEta","trackJetPt","vertexCategory","vertexLeptonCategory","trackSip2dSig","trackSip3dSig","trackSip2dVal","trackSip3dVal","trackMomentum","trackEta","trackPtRel","trackPPar","trackEtaRel","trackDeltaR","trackPtRatio","trackPParRatio","trackJetDist","trackDecayLenVal","vertexMass","vertexNTracks","vertexEnergyRatio","trackSip2dSigAboveCharm","trackSip3dSigAboveCharm","flightDistance2dSig","flightDistance3dSig","flightDistance2dVal","flightDistance3dVal","trackSumJetEtRatio","jetNSecondaryVertices","vertexJetDeltaR","trackSumJetDeltaR","jetNTracks","trackSip2dValAboveCharm","trackSip3dValAboveCharm","vertexFitProb","massVertexEnergyFraction","vertexBoostOverSqrtJetPt","chargedHadronEnergyFraction","neutralHadronEnergyFraction","photonEnergyFraction","electronEnergyFraction","muonEnergyFraction","chargedHadronMultiplicity","neutralHadronMultiplicity","photonMultiplicity","electronMultiplicity","muonMultiplicity","hadronMultiplicity","hadronPhotonMultiplicity","totalMultiplicity"
)),
		cms.untracked.PSet( label = cms.untracked.string("CombinedSVPseudoVertexNoSoftLepton"),  variables=cms.untracked.vstring(
"jetPt","jetEta","trackJetPt","vertexCategory","vertexLeptonCategory","trackSip2dSig","trackSip3dSig","trackSip2dVal","trackSip3dVal","trackMomentum","trackEta","trackPtRel","trackPPar","trackEtaRel","trackDeltaR","trackPtRatio","trackPParRatio","trackJetDist","trackDecayLenVal","vertexMass","vertexNTracks","vertexEnergyRatio","trackSip2dSigAboveCharm","trackSip3dSigAboveCharm","trackSumJetEtRatio","vertexJetDeltaR","trackSumJetDeltaR","jetNTracks","trackSip2dValAboveCharm","trackSip3dValAboveCharm","massVertexEnergyFraction","vertexBoostOverSqrtJetPt","chargedHadronEnergyFraction","neutralHadronEnergyFraction","photonEnergyFraction","electronEnergyFraction","muonEnergyFraction","chargedHadronMultiplicity","neutralHadronMultiplicity","photonMultiplicity","electronMultiplicity","muonMultiplicity","hadronMultiplicity","hadronPhotonMultiplicity","totalMultiplicity"
)),
		cms.untracked.PSet( label = cms.untracked.string("CombinedSVNoVertexNoSoftLepton"),  variables=cms.untracked.vstring(
"jetPt","jetEta","trackJetPt","vertexCategory","vertexLeptonCategory","trackSip2dSig","trackSip3dSig","trackSip2dVal","trackSip3dVal","trackMomentum","trackEta","trackPtRel","trackPPar","trackEtaRel","trackDeltaR","trackPtRatio","trackPParRatio","trackJetDist","trackDecayLenVal","trackSip2dSigAboveCharm","trackSip3dSigAboveCharm","trackSumJetEtRatio","trackSumJetDeltaR","jetNTracks","trackSip2dValAboveCharm","trackSip3dValAboveCharm","chargedHadronEnergyFraction","neutralHadronEnergyFraction","photonEnergyFraction","electronEnergyFraction","muonEnergyFraction","chargedHadronMultiplicity","neutralHadronMultiplicity","photonMultiplicity","electronMultiplicity","muonMultiplicity","hadronMultiplicity","hadronPhotonMultiplicity","totalMultiplicity"
)), # no trackEtaRel!!!???!!!
		cms.untracked.PSet( label = cms.untracked.string("CombinedSVRecoVertexSoftMuon"),  variables=cms.untracked.vstring(
"jetPt","jetEta","trackJetPt","vertexCategory","vertexLeptonCategory","trackSip2dSig","trackSip3dSig","trackSip2dVal","trackSip3dVal","trackMomentum","trackEta","trackPtRel","trackPPar","trackEtaRel","trackDeltaR","trackPtRatio","trackPParRatio","trackJetDist","trackDecayLenVal","vertexMass","vertexNTracks","vertexEnergyRatio","trackSip2dSigAboveCharm","trackSip3dSigAboveCharm","flightDistance2dSig","flightDistance3dSig","flightDistance2dVal","flightDistance3dVal","trackSumJetEtRatio","jetNSecondaryVertices","vertexJetDeltaR","trackSumJetDeltaR","jetNTracks","trackSip2dValAboveCharm","trackSip3dValAboveCharm","vertexFitProb","massVertexEnergyFraction","vertexBoostOverSqrtJetPt","leptonPtRel","leptonSip3d","leptonDeltaR","leptonRatioRel","leptonEtaRel","leptonRatio","chargedHadronEnergyFraction","neutralHadronEnergyFraction","photonEnergyFraction","electronEnergyFraction","muonEnergyFraction","chargedHadronMultiplicity","neutralHadronMultiplicity","photonMultiplicity","electronMultiplicity","muonMultiplicity","hadronMultiplicity","hadronPhotonMultiplicity","totalMultiplicity"
)),
		cms.untracked.PSet( label = cms.untracked.string("CombinedSVPseudoVertexSoftMuon"),  variables=cms.untracked.vstring(
"jetPt","jetEta","trackJetPt","vertexCategory","vertexLeptonCategory","trackSip2dSig","trackSip3dSig","trackSip2dVal","trackSip3dVal","trackMomentum","trackEta","trackPtRel","trackPPar","trackEtaRel","trackDeltaR","trackPtRatio","trackPParRatio","trackJetDist","trackDecayLenVal","vertexMass","vertexNTracks","vertexEnergyRatio","trackSip2dSigAboveCharm","trackSip3dSigAboveCharm","trackSumJetEtRatio","vertexJetDeltaR","trackSumJetDeltaR","jetNTracks","trackSip2dValAboveCharm","trackSip3dValAboveCharm","massVertexEnergyFraction","vertexBoostOverSqrtJetPt","leptonPtRel","leptonSip3d","leptonDeltaR","leptonRatioRel","leptonEtaRel","leptonRatio","chargedHadronEnergyFraction","neutralHadronEnergyFraction","photonEnergyFraction","electronEnergyFraction","muonEnergyFraction","chargedHadronMultiplicity","neutralHadronMultiplicity","photonMultiplicity","electronMultiplicity","muonMultiplicity","hadronMultiplicity","hadronPhotonMultiplicity","totalMultiplicity"
)),
		cms.untracked.PSet( label = cms.untracked.string("CombinedSVNoVertexSoftMuon"),  variables=cms.untracked.vstring(
"jetPt","jetEta","trackJetPt","vertexCategory","vertexLeptonCategory","trackSip2dSig","trackSip3dSig","trackSip2dVal","trackSip3dVal","trackMomentum","trackEta","trackPtRel","trackPPar","trackDeltaR","trackPtRatio","trackPParRatio","trackJetDist","trackDecayLenVal","trackSip2dSigAboveCharm","trackSip3dSigAboveCharm","trackSumJetEtRatio","trackSumJetDeltaR","jetNTracks","trackSip2dValAboveCharm","trackSip3dValAboveCharm","leptonPtRel","leptonSip3d","leptonDeltaR","leptonRatioRel","leptonEtaRel","leptonRatio","chargedHadronEnergyFraction","neutralHadronEnergyFraction","photonEnergyFraction","electronEnergyFraction","muonEnergyFraction","chargedHadronMultiplicity","neutralHadronMultiplicity","photonMultiplicity","electronMultiplicity","muonMultiplicity","hadronMultiplicity","hadronPhotonMultiplicity","totalMultiplicity"
)), # no trackEtaRel!!!???!!!,"vertexNTracks"
		cms.untracked.PSet( label = cms.untracked.string("CombinedSVRecoVertexSoftElectron"),  variables=cms.untracked.vstring(
"jetPt","jetEta","trackJetPt","vertexCategory","vertexLeptonCategory","trackSip2dSig","trackSip3dSig","trackSip2dVal","trackSip3dVal","trackMomentum","trackEta","trackPtRel","trackPPar","trackEtaRel","trackDeltaR","trackPtRatio","trackPParRatio","trackJetDist","trackDecayLenVal","vertexMass","vertexNTracks","vertexEnergyRatio","trackSip2dSigAboveCharm","trackSip3dSigAboveCharm","flightDistance2dSig","flightDistance3dSig","flightDistance2dVal","flightDistance3dVal","trackSumJetEtRatio","jetNSecondaryVertices","vertexJetDeltaR","trackSumJetDeltaR","jetNTracks","trackSip2dValAboveCharm","trackSip3dValAboveCharm","vertexFitProb","massVertexEnergyFraction","vertexBoostOverSqrtJetPt","leptonPtRel","leptonSip3d","leptonDeltaR","leptonRatioRel","leptonEtaRel","leptonRatio","chargedHadronEnergyFraction","neutralHadronEnergyFraction","photonEnergyFraction","electronEnergyFraction","muonEnergyFraction","chargedHadronMultiplicity","neutralHadronMultiplicity","photonMultiplicity","electronMultiplicity","muonMultiplicity","hadronMultiplicity","hadronPhotonMultiplicity","totalMultiplicity"
)),
		cms.untracked.PSet( label = cms.untracked.string("CombinedSVPseudoVertexSoftElectron"),  variables=cms.untracked.vstring(
"jetPt","jetEta","trackJetPt","vertexCategory","vertexLeptonCategory","trackSip2dSig","trackSip3dSig","trackSip2dVal","trackSip3dVal","trackMomentum","trackEta","trackPtRel","trackPPar","trackEtaRel","trackDeltaR","trackPtRatio","trackPParRatio","trackJetDist","trackDecayLenVal","vertexMass","vertexNTracks","vertexEnergyRatio","trackSip2dSigAboveCharm","trackSip3dSigAboveCharm","trackSumJetEtRatio","vertexJetDeltaR","trackSumJetDeltaR","jetNTracks","trackSip2dValAboveCharm","trackSip3dValAboveCharm","massVertexEnergyFraction","vertexBoostOverSqrtJetPt","leptonPtRel","leptonSip3d","leptonDeltaR","leptonRatioRel","leptonEtaRel","leptonRatio","chargedHadronEnergyFraction","neutralHadronEnergyFraction","photonEnergyFraction","electronEnergyFraction","muonEnergyFraction","chargedHadronMultiplicity","neutralHadronMultiplicity","photonMultiplicity","electronMultiplicity","muonMultiplicity","hadronMultiplicity","hadronPhotonMultiplicity","totalMultiplicity"
)),
		cms.untracked.PSet( label = cms.untracked.string("CombinedSVNoVertexSoftElectron"),  variables=cms.untracked.vstring(
"jetPt","jetEta","trackJetPt","vertexCategory","vertexLeptonCategory","trackSip2dSig","trackSip3dSig","trackSip2dVal","trackSip3dVal","trackMomentum","trackEta","trackPtRel","trackPPar","trackDeltaR","trackPtRatio","trackPParRatio","trackJetDist","trackDecayLenVal","trackSip2dSigAboveCharm","trackSip3dSigAboveCharm","trackSumJetEtRatio","trackSumJetDeltaR","jetNTracks","trackSip2dValAboveCharm","trackSip3dValAboveCharm","leptonPtRel","leptonSip3d","leptonDeltaR","leptonRatioRel","leptonEtaRel","leptonRatio","chargedHadronEnergyFraction","neutralHadronEnergyFraction","photonEnergyFraction","electronEnergyFraction","muonEnergyFraction","chargedHadronMultiplicity","neutralHadronMultiplicity","photonMultiplicity","electronMultiplicity","muonMultiplicity","hadronMultiplicity","hadronPhotonMultiplicity","totalMultiplicity"
)) # no trackEtaRel!!!???!!!

	),
	ipTagInfos = cms.InputTag("impactParameterTagInfos"),
#	svTagInfos =cms.InputTag("secondaryVertexTagInfos"),
	svTagInfos =cms.InputTag("inclusiveSecondaryVertexFinderTagInfos"),
	muonTagInfos =cms.InputTag("softPFMuonsTagInfos"),
	elecTagInfos =cms.InputTag("softPFElectronsTagInfos"),
	
	
	minimumTransverseMomentum = cms.double(15.0),
	maximumTransverseMomentum = cms.double(9999999.),
	useCategories = cms.bool(True),
  calibrationRecords = cms.vstring(
		'CombinedSVRecoVertexNoSoftLepton', 
		'CombinedSVPseudoVertexNoSoftLepton', 
		'CombinedSVNoVertexNoSoftLepton',
		'CombinedSVRecoVertexSoftMuon', 
		'CombinedSVPseudoVertexSoftMuon', 
		'CombinedSVNoVertexSoftMuon',
		'CombinedSVRecoVertexSoftElectron', 
		'CombinedSVPseudoVertexSoftElectron', 
		'CombinedSVNoVertexSoftElectron'),
	categoryVariableName = cms.string('vertexLeptonCategory'), # vertexCategory = Reco,Pseudo,No
	maximumPseudoRapidity = cms.double(2.5),
	signalFlavours = cms.vint32(5, 7),
	minimumPseudoRapidity = cms.double(0.0),
	jetTagComputer = cms.string('combinedSecondaryVertexSoftLeptonComputer'),
	jetFlavourMatching = cms.InputTag("jetFlavourInfosAK4PFJets"),
	matchedGenJets = cms.InputTag("matchedAK4PFGenJets"),
	ignoreFlavours = cms.vint32(0)
)


process.p = cms.Path(
process.selectedAK4PFGenJets*
process.matchedAK4PFGenJets *
process.goodOfflinePrimaryVertices * 
process.inclusiveVertexing * 
#process.inclusiveMergedVerticesFiltered * 
#process.bToCharmDecayVertexMerged * 
process.myak4JetTracksAssociatorAtVertex * 
process.impactParameterTagInfos * 
#process.secondaryVertexTagInfos * 
process.inclusiveSecondaryVertexFinderTagInfos *
process.softPFMuonsTagInfos *
process.softPFElectronsTagInfos *
process.selectedHadronsAndPartons *
process.jetFlavourInfosAK4PFJets *
process.combinedSVMVATrainer 
)
