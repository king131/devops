内存使用率较高时，有可能是大量的buffer／cache占用
---
```bash
#!/bin/bash
#get memory info       
phymem=`free | grep "Mem:" |awk '{print $2}'`
phymemused=`free | grep 'buffers/cache' | awk '{print $3}'`
#get memory use Utilization 
UTILIZATION=`awk 'BEGIN{printf"%d\n",('$phymemused'/'$phymem')*100}'`
if [ $UTILIZATION -gt 85 ];then
    echo "UTILIZATION=$UTILIZATION"
    echo 3 > /proc/sys/vm/drop_caches
    echo 0 > /proc/sys/vm/drop_caches
    sync
fi
```
