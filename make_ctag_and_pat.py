from PhysicsTools.PatAlgos.patTemplate_cfg import *
import os
## switch to uncheduled mode
if not os.path.isdir('trees'):
   os.path.makedirs('trees')

process.MessageLogger.cerr.FwkReport.reportEvery = 100
process.options.allowUnscheduled = cms.untracked.bool(True)
process.options.wantSummary = True
#process.Tracer = cms.Service("Tracer")

## load tau sequences up to selectedPatJets
process.load("PhysicsTools.PatAlgos.producersLayer1.jetProducer_cff")
process.load("PhysicsTools.PatAlgos.selectionLayer1.jetSelector_cfi")

process.load('RecoBTag/Configuration/RecoBTag_cff')
## process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
## from Configuration.AlCa.GlobalTag import GlobalTag
## process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc')

process.softPFElectronsTagInfos.useMCpromptElectronFilter = cms.bool(True)
process.softPFMuonsTagInfos.useMCpromptElectronFilter = cms.bool(True)

## Events to process
process.maxEvents.input = 1000 #1000
process.out.fileName = 'trees/validate_ctag_pat.root'

process.patJetCorrFactors.levels = []
## Input files
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
      'file:~/nobackup/RelValTTbar_13_sample.root',
    )
)

#store debugging
process.charmTagsComputerCvsL.debugFile = cms.string('trees/ctag_debug_CvsL.root')
process.charmTagsComputerCvsB.debugFile = cms.string('trees/ctag_debug_CvsB.root')
process.charmTagsComputerCvsL.tagInfos = cms.VInputTag(
   cms.InputTag("pfImpactParameterTagInfos"), 
   cms.InputTag("pfInclusiveSecondaryVertexFinderCtagLTagInfos"), 
   cms.InputTag("softPFMuonsTagInfos"    , '', 'PAT'), 
   cms.InputTag("softPFElectronsTagInfos", '', 'PAT')
   )
process.charmTagsComputerCvsB.tagInfos = cms.VInputTag(
   cms.InputTag("pfImpactParameterTagInfos"), 
   cms.InputTag("pfInclusiveSecondaryVertexFinderCtagLTagInfos"), 
   cms.InputTag("softPFMuonsTagInfos"    , '', 'PAT'), 
   cms.InputTag("softPFElectronsTagInfos", '', 'PAT')
   )



## Output file
process.out.outputCommands.append('keep *_goodOfflinePrimaryVertices_*_*')

#select good primary vertex
from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
process.goodOfflinePrimaryVertices = cms.EDFilter(
    "PrimaryVertexObjectFilter",
    filterParams = pvSelector.clone( minNdof = cms.double(4.0), maxZ = cms.double(24.0) ),
    src=cms.InputTag('offlinePrimaryVertices'),
    filter=cms.bool(False)
    )

#process.p = cms.Path(
#    process.pfCTagging
#)

