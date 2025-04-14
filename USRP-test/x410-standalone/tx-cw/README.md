
## Setup for build
Install packages: `sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu`


## Build
First cd to the directory: `cd USRP-test/x410-standalone/tx-cw/`
Run: `make`

## Depoly
Run: `scp cw_tx root@<x410_ip>:~/G611/`

Start the application: 
1. ssh to the x410: `root@<x410_ip>`
2. Start application: `./G611/cw_tx`