This folder contains Bro Scripts and Bro functions for parsing, evaluating and dissecting pcap files containing IEC-104 packets.

Useful bash snippets:

Run bro in docker with pcap-file (Example):
```bash
cd /data/scripts && bro -C -r /data/pcap/traffic.pcap t104.evt T104_STATS_Events.bro
```

Alternative (2 bash shells in same docker container):
```bash
bro -i eth0 -C T104_STATS_Events.bro t104.evt 
# Wait for "Listening on eth0.". Then:
tcpreplay --pps 1000 --intf1=eth0 /data/pcap/traffic.pcap
```

Run broccoli-python bindings over pcap-file (3 bash shells):
```bash
cd /data/scripts/ && bro -i eth0 -C T104_Broccoli.bro t104.evt 
# Wait for "Listening on eth0.". Then:
cd /data/scripts/ && python T104_BroccoliInterface.py
# Wait for "Connected.". Then:
tcpreplay --pps 1000 --intf1=eth0 /data/pcap/traffic.pcap
```