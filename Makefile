build:
	@sudo docker build -t lirios/unstable .

all: build

.PHONY: build
