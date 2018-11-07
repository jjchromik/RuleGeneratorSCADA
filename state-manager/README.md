This folder contains the Python scripts for the prototype. It contains 1) the topology 2) the state manager and 3) the event engine.
Futhermore, the interface to the prototype's second component, Bro, is built into the event engine. All scenario files are included in this folder.

The analysis of the electrical grid's state is separated into safety and consistency rules. The model used for those rules is based on the following work:
Chromik, J. J., Remke, A., & Haverkort, B. R. (2016). Improving SCADA security of a local process with a power grid model. Proceedings of the 4th International Symposium for ICS & SCADA Cyber Security Research 2016, 114–123.

Analyze scenarios that are given in traffic capture files (3 different interactive bash shells in docker container):
```bash
# First shell:
cd /data/pythontests/ && bro -i eth0 -C T104_BroccoliStateManager_Masterthesis.bro t104.evt
# Second shell:
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
# Usage: (Asynchronous key polling): <d>ebug, <i>nfo, <w>arnings, <a>utomatic evaluation on/off, <c>lose, <v>alues print, <e>valuate current state, <s> save state, <l> load state
```