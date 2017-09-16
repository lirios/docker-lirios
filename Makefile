build:
	@sudo docker build -t lirios/unstable --build-arg today=$(date +%s) .

push:
	@sudo docker push lirios/unstable

all: build

.PHONY: build
