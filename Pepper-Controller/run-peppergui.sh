# Prerequisites
#   brew install xquartz
    
# Set your Mac IP address
ip=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')

# Allow connections from Mac to XQuartz
/opt/X11/bin/xhost + $ip

# Run container
docker run -it --rm --env="DISPLAY=host.docker.internal:0" -host pepperdoc