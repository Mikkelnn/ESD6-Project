## Tools needed
1) Ensure ISE 14.7 is installed with a valid license
Ensure a networkcard has the name "eth0" and the MAC-address from that card is used for the license.
On linux follow thease instruction (scoll to the bottom):
https://kb.ettus.com/RFNoC_(UHD_3.0)#Xilinx_License:_Xilinx.E2.80.99s_License_manager_looks_for_an_Ethernet_adapter_with_the_name_eth0


## Build custom image for B205mini
1) run: `cd USRP-test/FPGA-test/usrp3/top/b2xxmini` 
2) run: `make B205mini` if error try `make clean && make B205mini`


## Load image to B205mini
1) Connect with USB
2) run: `LD_LIBRARY_PATH= uhd_image_loader --args="type=b200" --fpga-path=build/usrp_b205mini_fpga.bit`
