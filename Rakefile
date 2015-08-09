$cmssw = ENV['CMSSW_BASE']+'/src/'
$project_dir = ENV['CMSSW_BASE']+'/src/CTagValidation/'

file 'trees/validate_ctag_pat.root' => 'make_ctag_and_pat.py' do |t|
  sh 'cmsRun make_ctag_and_pat.py'
end

task :pattree => ['trees/validate_ctag_pat.root'] do |t|
end

file 'training_trees/CombinedSVRecoVertexSoftMuon_DUSG.root' => 'varextractor_cfg.py' do |t|
  sh 'cmsRun varextractor_cfg.py'
  sh './merge_into_categories.sh'
  sh 'rm CombinedSV*.root'
  #remove spurious file that has no events inside
  sh 'rm training_trees/CombinedSVPseudoVertexSoftMuon_DUSG.root'
end

file 'flat_trees/CombinedSVRecoVertexSoftElectron_B.root' => ['training_trees/CombinedSVRecoVertexSoftMuon_DUSG.root', "#{$cmssw}/TMVA_CTagging/createNewTree.py"] do |t|
  chdir("#{$cmssw}/TMVA_CTagging") do
    sh "python createNewTree.py"
  end
end

file 'trees/CombinedSV_ALL.root' => 'flat_trees/CombinedSVRecoVertexSoftElectron_B.root' do |t|
  sh "./merge_flat_into_all.sh"
end

task :flattree => ['trees/CombinedSV_ALL.root'] do |t|
end

file 'historanges.db' => ['set_plot_ranges.py', 'trees/CombinedSV_ALL.root', 'trees/validate_ctag_pat.root'] do |t|
  sh 'python set_plot_ranges.py'
end

file 'flat_jet_map' => ['make_jet_map.py', 'trees/CombinedSV_ALL.root', 'trees/validate_ctag_pat.root'] do |t|
  sh 'python make_jet_map.py'
end

file 'analyzed/flat_tree_output.root' => ['analyze_flat_trees.py', 'flat_jet_map', 'historanges.db', 'trees/CombinedSV_ALL.root'] do |t|
  sh 'python analyze_flat_trees.py'
end

file 'analyzed/pat_validation_output.root' => ['flat_jet_map', 'historanges.db', 'trees/validate_ctag_pat.root', 'analyze_pat.py'] do |t|
  sh 'python analyze_pat.py'
end

file 'analyzed/varex_output.root' => ['analyze_varex_trees.py', 'flat_jet_map', 'historanges.db', 'training_trees/CombinedSVRecoVertexSoftMuon_DUSG.root'] do |t|
  sh 'python analyze_varex_trees.py'
end

task :analyze => ['analyzed/pat_validation_output.root', 'analyzed/flat_tree_output.root', 'analyzed/varex_output.root'] do |t|
end

task :plots => [] do |t|
  sh 'python make_plots.py'
end

