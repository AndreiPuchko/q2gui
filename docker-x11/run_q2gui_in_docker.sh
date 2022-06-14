docker run --rm -it \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY=$DISPLAY \
    -u q2gui \
    q2gui \
    python3 demo/${1-demo_00.py} /ini:none
