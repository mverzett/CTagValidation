eval `scramv1 runtime -sh`
vpython=$CMSSW_BASE/src/CTagValidation/external/vpython

export VIRTUAL_ENV_DISABLE_PROMPT=1
pushd $vpython
source bin/activate
popd

export PYTHONPATH=$vpython/lib/python2.7/site-packages/:$PYTHONPATH
