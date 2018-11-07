This IEC-104 traffic generator can emulate valid/parsable IEC-104 traffic for a subset of function codes that are sufficient for traffic emulation (for testing and evaluating the prototype).
The generated traffic is sent on the local loopback network interface. As the traffic generator implements a full server/client connection, the result will be indistinguishable from real traffic (e.g., it contains TCP handshakes etcetera).

Create traffic file for a scenario (select scenario in AutomaticTrafficGeneration.py main function):
```bash
# Select scenarios in source code, then:
python AutomaticTrafficGeneration.py
```