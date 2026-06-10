#!/bin/bash
set -e

# Source the global ROS2 installation variables
source "/opt/ros/jazzy/setup.bash"

# Source the compiled workspace nodes if they exist (Prod stage fallback)
if [ -f "/workspace/object_aware_nav_ws/install/setup.bash" ]; then
  source "/workspace/object_aware_nav_ws/install/setup.bash"
fi

# Execute the command passed to the docker container
exec "$@"
