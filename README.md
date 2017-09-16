Liri OS Docker images
=====================

Daily images for Docker to try out Liri OS.

## Running

If you are running Xorg:

```sh
xhost +
```

Then on Xorg or Wayland:

```sh
sudo docker run --rm -it \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY=$DISPLAY \
    -e WAYLAND_DISPLAY=$WAYLAND_DISPLAY \
    --device=/dev/dri/card0:/dev/dri/card0 \
    --device=/dev/dri/controlD64:/dev/dri/controlD64 \
    --device=/dev/dri/renderD128:/dev/dri/renderD128 \
    lirios/unstable
```
