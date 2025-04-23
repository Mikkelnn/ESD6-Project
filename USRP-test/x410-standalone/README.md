
## Get cross compiled binaries and libaries for the ARM coretex A53
`cd` to current directory
Ensure the following folers are created:
 - x410-sysroot/include/
 - x410-sysroot/lib/

run the following command to copy nececery files:
- `rsync -avz root@<x410_ip>:/usr/include/uhd x410-sysroot/include/`
- `rsync -avz root@<x410_ip>:/usr/lib/libuhd.so* x410-sysroot/lib/`
