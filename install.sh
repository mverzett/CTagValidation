#! /bin/env bash

eval `scramv1 runtime -sh`

mkdir external/vpython
external=$CMSSW_BASE/src/CTagValidation/external
vpython=$external/vpython
vpy_src=$external/src/virtualenv

pushd $vpy_src
./virtualenv.py --distribute $vpython
popd

pushd $vpython
source bin/activate

pip install -e $external/src/rootpy

