This docker image extends the rsmrr/hilti image by intstalling broccoli with python bindings, tcpreplay and some other useful network tools. Tcpreplay can be used to run bro (and broccoli) in its normal listening mode while replaying previously captured pcap files.

Run docker:
```bash
docker run -i -t -v $(pwd)/workspace:/data "rf/broccoli-hilti"
```

Open additional shells:
```bash
docker exec -it $(docker container ls | grep rf/broccoli-hilti | awk '{ print $1 }' | head -1) bash
# Alternative (e.g. if you prefer not to make use of docker group membership and docker therefore requires sudo)
docker exec -it <Container-ID> bash
```

Build image rf/broccoli-hilti:
```bash
cd $(pwd)/docker && docker build -t rf/broccoli-hilti .
```

Test image. This should produce NO output (python import errors) at all:
```bash
docker run -t rf/broccoli-hilti python -c "import broccoli"
```