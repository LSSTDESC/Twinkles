#!/bin/bash

taskName=TW-phoSim-r3
pipelineRoot=/nfs/farm/g/desc/u1/Pipeline-tasks/${taskName}

GLOBIGNORE="*"
src=${pipelineRoot}/Twinkles/workflows/${taskName}/
des="${pipelineRoot}/config/"

echo src "${src}"
echo dst ${dst}

##cmd="rsync -avuzb  --exclude ""*~"" ${src} ${dst}"

## Create sym links in task/config directory to the repository
cmd="cp -as " ${src} ${dst}

echo cmd ${cmd}
${cmd}