build:
	@sudo docker build -t lirios/unstable --build-arg today=$(date +%s) --build-arg channel=unstable .

push:
	@sudo docker push lirios/unstable

all: build

.PHONY: build
