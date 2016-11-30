config.doUseRegister=False
config.convolveTemplate=True
config.doWriteMatchedExp=True
config.doDecorrelation=True

config.doMerge=True

config.subtract.kernel.name='AL'

from lsst.ip.diffim.getTemplate import GetCalexpAsTemplateTask
config.getTemplate.retarget(GetCalexpAsTemplateTask)

