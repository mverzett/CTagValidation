#! /bin/env bash

CAT=(CombinedSVRecoVertexNoSoftLepton CombinedSVPseudoVertexNoSoftLepton CombinedSVNoVertexNoSoftLepton CombinedSVRecoVertexSoftElectron CombinedSVPseudoVertexSoftElectron CombinedSVNoVertexSoftElectron CombinedSVRecoVertexSoftMuon CombinedSVPseudoVertexSoftMuon CombinedSVNoVertexSoftMuon )
#CAT=(CombinedSVRecoVertexNoSoftLepton CombinedSVPseudoVertexNoSoftLepton CombinedSVNoVertexNoSoftLepton CombinedSVRecoVertexSoftElectron CombinedSVNoVertexSoftElectron CombinedSVRecoVertexSoftMuon CombinedSVNoVertexSoftMuon )

for k in ${CAT[@]} ;
do
		hadd -f -O training_trees/${k}_DUSG.root varextractor_out/${k}_[DGUS].root 
		cp -v varextractor_out/${k}_[BC].root training_trees/.
done

