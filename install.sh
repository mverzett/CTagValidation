#! /bin/env bash

#if it has errors STOP!
set -o nounset
set -o errexit

#get packages will be modified
git cms-init

git cms-addpkg CommonTools/Utils              
git cms-addpkg DataFormats/BTauReco           
git cms-addpkg PhysicsTools/PatAlgos          
git cms-addpkg RecoBTag/CTagging              
git cms-addpkg RecoBTag/Configuration         
git cms-addpkg RecoBTag/SecondaryVertex       
git cms-addpkg RecoBTag/SoftLepton            
git cms-addpkg RecoBTau/JetTagComputer        
git cms-addpkg RecoVertex/AdaptiveVertexFinder


#get CTagging temporary repo
git remote add mauro https://github.com/mverzett/cmssw.git
git fetch mauro charm_tagging_v2

#cherry-pick everything (in the right order)
git cherry-pick 59e260c437e3a198ff059b1ce6b490572ab3d6d9
git cherry-pick 7d0ec2d188864cfcc56ab3e4279302cfcf293940
git cherry-pick 678ce8c1a611f7ab96975716476a395807f20851
git cherry-pick b446331baae29843db94f7bdc15fbc2cb86d6253
git cherry-pick c42b3030dbdfe2b666e747ec8ec1c038e2d7d77a
git cherry-pick 7c611f10a41e658dd3db939474e5804977b1ff9f
git cherry-pick 322b99b1c1b7039b4099862cacaace63f43b21bf
git cherry-pick 6088ba8fda0f60dcc97ccea2a17b50ea18f09736
git cherry-pick 5b220b1098dfccefe014a00c0ab578334c8ca035
git cherry-pick 4b15bb1733d91b99ccc5126e8c63ad3e3a6eb40d
git cherry-pick 26c949d85721589e526268f4fbc9515e12fc8044
git cherry-pick b17bf28194e3bd765d6cd687cbb7ee7bdb0ec412
git cherry-pick 27220e2be4e3cd82d2c18f7ae13f40c5fcdc2917
git cherry-pick aabde4971e941e93072b95ee0856d9e9e1d54c16
git cherry-pick 2e7a8687ae37127e471b98da2d9aab25afce8438
git cherry-pick 2648a5b5c2fade20f6ff124c08bddf339cf423d2
git cherry-pick fa4b3faad80da0ff17fcc7994df39e2b12e0a7fa
git cherry-pick 82ec1155d64b1fbd8c35e01bd72a458733e8c34d
git cherry-pick 27dd52ddc5e78fb3f6d6ab848f72f214cf00825d
git cherry-pick 60d2d5f576667db2736b8b82329fc0c92e765a5c
git cherry-pick abeb6e51d80598a90b2f463fc3c82bb83fb23f5d
git cherry-pick 7cca16c700ea05105fdc9e3c4c549e970a773727
git cherry-pick 057ef9f4814ec9977915ba1c2f2bd52c8acecc97
git cherry-pick 59f796324c0fcb86e669e3207896da64525dbe07
git cherry-pick 1fe098870a98f2c8801cf792cc7531aae493913d
git cherry-pick b5fa1eb6bcda1c36ee8f2b904aab0c7913e133fe
git cherry-pick 22ef935130bebf88ee03a70a38d423cf199e3bf6
git cherry-pick 78249b335d79d08612f522692858c99d7e900ad6
git cherry-pick d24c9c550e64265dc321921d6a614413fead9b8a
git cherry-pick f7a8d69a3c78fa63bb30543df2c59cf246ff1b6d
git cherry-pick 90ae1481826bad00d4b6fe53529d2f9160e5936f
git cherry-pick d3e73e1a9314ab46e971e43d46c61734acdd88d1
git cherry-pick 81800611e2b1b40f368dd5e1af209bc91b3ecb9a
