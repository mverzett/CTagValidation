from PhysicsTools.PatAlgos.patTemplate_cfg import *
import os
## switch to uncheduled mode
if not os.path.isdir('trees'):
   os.path.makedirs('trees')

process.options.allowUnscheduled = cms.untracked.bool(True)
#process.Tracer = cms.Service("Tracer")

## load tau sequences up to selectedPatJets
process.load("PhysicsTools.PatAlgos.producersLayer1.jetProducer_cff")
process.load("PhysicsTools.PatAlgos.selectionLayer1.jetSelector_cfi")

process.load('RecoBTag/Configuration/RecoBTag_cff')
## process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
## from Configuration.AlCa.GlobalTag import GlobalTag
## process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc')

## Events to process
process.maxEvents.input = 1000
process.out.fileName = 'trees/validate_ctag_pat_1ev.root'


## Input files
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
      '/store/relval/CMSSW_7_5_0_pre5/RelValTTbar_13/GEN-SIM-RECO/MCRUN2_75_V5-v1/00000/383E39B7-BA0B-E511-A509-0025905B8582.root',
      '/store/relval/CMSSW_7_5_0_pre5/RelValTTbar_13/GEN-SIM-RECO/MCRUN2_75_V5-v1/00000/4AE0AEB0-BA0B-E511-86F9-002618943857.root',
      '/store/relval/CMSSW_7_5_0_pre5/RelValTTbar_13/GEN-SIM-RECO/MCRUN2_75_V5-v1/00000/F0BEEE9E-120B-E511-88DD-0025905A60C6.root'
    )
)

## Output file
process.out.outputCommands.append('keep *_goodOfflinePrimaryVertices_*_*')

#select good primary vertex
from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
process.goodOfflinePrimaryVertices = cms.EDFilter(
    "PrimaryVertexObjectFilter",
    filterParams = pvSelector.clone( minNdof = cms.double(4.0), maxZ = cms.double(24.0) ),
    src=cms.InputTag('offlinePrimaryVertices'),
    filter=cms.bool(True)
    )

#process.p = cms.Path(
#    process.pfCTagging
#)

