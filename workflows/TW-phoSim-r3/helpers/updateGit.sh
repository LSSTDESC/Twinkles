#!/bin/bash

taskName=TW-phoSim-r3
pipelineRoot=/nfs/farm/g/desc/u1/Pipeline-tasks/${taskName}

GLOBIGNORE="*"
src="${pipelineRoot}/config/"
dst=${pipelineRoot}/Twinkles/workflows/${taskName}/

echo src "${src}"
echo dst ${dst}

cmd="rsync -avuzb  --exclude ""*~"" ${src} ${dst}"
echo cmd ${cmd}
${cmd}