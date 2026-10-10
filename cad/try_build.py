import time
from cad import skull
t=time.time()
h=skull.build_head(); print('head', time.time()-t)
for k,v in h.items():
    bb=v.BoundingBox(); print(k, round(v.Volume()/1000,1),'cm3', [round(x,1) for x in (bb.xlen,bb.ylen,bb.zlen)], v.isValid())
t=time.time(); j=skull.build_jaw(); print('jaw', time.time()-t, round(j.Volume()/1000,1), j.isValid())
