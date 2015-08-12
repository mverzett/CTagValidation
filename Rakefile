$cmssw = ENV['CMSSW_BASE']+'/src/'
$project_dir = ENV['CMSSW_BASE']+'/src/CTagValidation/'

file 'trees/validate_ctag_pat.root' => 'make_ctag_and_pat.py' do |t|
  sh 'cmsRun make_ctag_and_pat.py'
end

task :pattree => ['trees/validate_ctag_pat.root'] do |t|
end

file 'training_trees/CombinedSVRecoVertexSoftMuon_DUSG.root' => 'varextractor_cfg.py' do |t|
  sh 'rm -f training_trees/*.root'
  sh 'rm -f varextractor_out/*.root'
  sh 'cmsRun varextractor_cfg.py'
  sh 'mv CombinedSV*.root varextractor_out/.'
  sh './merge_into_categories.sh'
  #remove spurious file that has no events inside
  sh 'rm -f training_trees/CombinedSVPseudoVertexSoftMuon_DUSG.root'
end

file 'flat_trees/CombinedSVRecoVertexSoftElectron_B.root' => ['training_trees/CombinedSVRecoVertexSoftMuon_DUSG.root', "#{$cmssw}/TMVA_CTagging/createNewTree.py"] do |t|
  sh 'rm -f flat_trees/*.root'
  chdir("#{$cmssw}/TMVA_CTagging") do
    sh "python createNewTree.py"
  end
end

file 'trees/CombinedSV_ALL.root' => 'flat_trees/CombinedSVRecoVertexSoftElectron_B.root' do |t|
  sh "./merge_flat_into_all.sh"
end

task :flattree => ['trees/CombinedSV_ALL.root'] do |t|
end

task :trees => [:pattree, :flattree] do |t|
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

task :jetbyjet => [] do |t|
  sh 'python analyze_jetByjet.py'
end

task :plots => [] do |t|
  sh 'python make_plots.py'
end

task :diff => [] do |t|
  sh 'python make_diff_plots.py'
end

task :clean_flat => [] do |t|
  sh 'rm -f varextractor_out/*.root'
  sh 'rm -f flat_trees/*.root'
  sh 'rm -f training_trees/*.root'
  sh 'rm -f trees/CombinedSV_ALL.root'
  sh 'rm -f analyzed/flat_tree_output.root'
end

task :clean_pat => [] do |t|
  sh 'rm -f trees/ctag_debug_*.root trees/validate_ctag_pat.root'
  sh 'rm -f analyzed/pat_validation_output.root'
end

task :clean => [:clean_flat, :clean_pat] do |t|
  sh 'rm -f analyzed/*.*'
end

task :pubplots => [] do |t|
  sh "cp -r plots_#{ENV['tag']} ~/public_html/ctagdev/validation/."
  sh "find ~/public_html/ctagdev/validation/plots_#{ENV['tag']} -name *.pdf | xargs rm"
  sh '~/.bin/web.py ~/public_html/ctagdev/validation/'
end

task :pubdiffs => [] do |t|
  sh "cp -r diff_#{ENV['tag']} ~/public_html/ctagdev/validation/."
  sh "find ~/public_html/ctagdev/validation/diff_#{ENV['tag']} -name *.pdf | xargs rm"
  sh '~/.bin/web.py ~/public_html/ctagdev/validation/'
end
