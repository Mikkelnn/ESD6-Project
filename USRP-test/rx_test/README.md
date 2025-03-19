## Get USRP x310 running
1) In SFP port 0 connect SFP DAC-cable to a media converter and then ethernet to a PC
2) Ensure the pc's ethernet IP address is set to 192.168.10.x netmask: 255.255.255.0 (x310 has 192.168.10.2)
3) Connect a usb cable between the x310 and the pc (used to load the FPGA image)
4) Load the fpga image located in "USRP-test/rx_test/pre_synthesized_FPGA_images/usrp_x310_fpga_HG.bit" 
    or "/usr/share/uhd/4.8.0/images/usrp_x310_fpga_HG.bit" 
    using vivado programmer (Hardwarre manager -> auto connect -> program device)
5) The green LED on the SFP port 0 on the x310 should now light green
6) Ensure it is possible to ping the x310 (ping 192.168.10.2)
7) Open the desired flowgraph in GnuRadio and run it :)
