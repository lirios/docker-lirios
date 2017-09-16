build:
	@sudo docker build -t lirios/unstable .

push:
	@sudo docker push lirios/unstable

all: build

.PHONY: build
