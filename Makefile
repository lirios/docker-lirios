base:
	@(cd base; sudo ./mkimage-arch.sh)

build:
	@sudo docker build -t lirios/unstable .

all: base build

.PHONY: base build
