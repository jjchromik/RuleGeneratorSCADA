# Master thesis: A prototype implementation for process-aware intrusion detection in electrical grids (IEC-60870-5-104, Bro)

## Overview
This project is a prototype implementation of a process-aware, network-based intrusion detection which generates rules from physical process descriptions and RTU configurations. It uses an electrical grid model to evaluate a set of consistency and safety rules that were defined in the master thesis. The prototype works with Bro, which is the process variable source for the intrusion detection model. Values are obtained from network traffic, which contains IEC-60870-5-104 (short: IEC-104) control traffic. Bro parses, interprets and converts the raw traffic's contents according to an RTU configuration and triggers events via broccoli in the protocol-independent Python component of the IDS.

**Note: Command examles for all components can be found below and in the CheatSheet file!**

The Python component is located in the directory **state-manager**. You can find the state-manager, the topology and the event engine there. Also the necessary Bro scripts, which create the broccoli-interface, can be found in this folder. Finally, scenario files are also located in this directory to faciliate testing.

The folder **bro-scripts** contains the Bro components of the IDS like the parser and defined IEC-104 Bro events. There are additionally more scripts for analyzing IEC-104 traffic regarding function codes, measurements and commands. Also, performance tests are included. Most of the code is IEC-60870-5-104-specific.

The **traffic-generator** takes scenario files and an RTU configuration and emulates valid IEC-104 control traffic on a local network interface. It automatically generated .pcap files from scenarios for testing purposes.

The project provides a **policy-generator** to translate common RTU configuration files into Bro scripts for converting, normalizing and interpreting the obtained raw values from IEC-104 traffic. 

The directory **docker** provides a docker image definition, which can be used to process pcap files with bro and broccoli-python bindings. Furthermore, many network diagnosis and utility tools are installed (like tcpdump, tcpreplay etc.). All required files for a quick start can be found in the **workspace** folder. This folder is mounted by the analysis example below and acts as a minimal working example.

The energy grid model and the rules are based on the following paper:
Chromik, J. J., Remke, A., & Haverkort, B. R. (2016). Improving SCADA security of a local process with a power grid model. Proceedings of the 4th International Symposium for ICS & SCADA Cyber Security Research 2016, 114–123.

## Preparation (Docker)
Build docker image rf/broccoli-hilti:
```bash
cd /path/to/this/repo
cd docker && docker build -t rf/broccoli-hilti .
```
Test image (this should produce NO output at all):
```bash
docker run -t rf/broccoli-hilti python -c "import broccoli"
```
Run docker:
```bash
docker run -i -t -v $(pwd)/workspace:/data "rf/broccoli-hilti"
```
Open additional shells:
```bash
docker container ls
docker exec -it <containerID> bash
```
Alternative (requires permission to run docker without sudo password):
```bash
docker exec -it $(docker container ls | grep rf/broccoli-hilti | awk '{ print $1 }' | head -1) bash
```

## Analysis (Requires: 3 docker bash shells)
Analyze scenarios that are given in traffic capture files (3 different interactive bash shells in the same docker container):
```bash
# First shell:
cd /data/pythontests/ && bro -i eth0 -C T104_BroccoliStateManager_Masterthesis.bro t104.evt
# Second shell (wait until first shell prints "listening on eth0"):
cd /data/pythontests/ && python TestScenariosBroMasterthesis.py
# Replay traffic:
tcpreplay --intf1=eth0 /data/pcap/scenarios/Masterthesis_GlobalKnowledge_Normalized_Scenario1.pcapng
tcpreplay --intf1=eth0 /data/pcap/scenarios/Masterthesis_GlobalKnowledge_Normalized_Scenario2.pcapng
tcpreplay --intf1=eth0 /data/pcap/scenarios/Masterthesis_GlobalKnowledge_Normalized_Scenario3.pcapng
tcpreplay --intf1=eth0 /data/pcap/scenarios/Masterthesis_GlobalKnowledge_Normalized_Scenario4.pcapng
tcpreplay --intf1=eth0 /data/pcap/scenarios/Masterthesis_GlobalKnowledge_Normalized_Scenario5.pcapng
tcpreplay --intf1=eth0 /data/pcap/scenarios/Masterthesis_GlobalKnowledge_Normalized_Scenario6.pcapng
tcpreplay --intf1=eth0 /data/pcap/scenarios/Masterthesis_GlobalKnowledge_Normalized_Scenario7.pcapng
tcpreplay --intf1=eth0 /data/pcap/scenarios/Masterthesis_GlobalKnowledge_Normalized_Scenario8.pcapng
tcpreplay --intf1=eth0 /data/pcap/scenarios/Masterthesis_GlobalKnowledge_Normalized_Scenario9.pcapng
# Keyboard commands: (Asynchronous key polling): 
# <d>ebug, <i>nfo, <w>arnings, <a>utomatic evaluation on/off, <c>lose, <v>alues print, <e>valuate current state, <s> save state, <l> load state
```