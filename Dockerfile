# ============================================================================
# STAGE 1: Base Runtime (NVIDIA GPU + ROS2 Jazzy Core)
# ============================================================================
FROM osrf/ros:jazzy-desktop-full AS base

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install critical system and hardware acceleration dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    lsb-release \
    software-properties-common \
    mesa-utils \
    libgl1 \
    libgl1-mesa-dri \
    && rm -rf /var/lib/apt/lists/*

# Environment variables for NVIDIA Container Toolkit GUI forwarding
ENV NVIDIA_VISIBLE_DEVICES=${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES=${NVIDIA_DRIVER_CAPABILITIES:-all}
ENV __NV_PRIME_RENDER_OFFLOAD=1
ENV __GLX_VENDOR_LIBRARY_NAME=nvidia

# Setup ROS2 entrypoint script
COPY ./ros_entrypoint.sh /ros_entrypoint.sh
RUN chmod +x /ros_entrypoint.sh
ENTRYPOINT ["/ros_entrypoint.sh"]

# ============================================================================
# STAGE 2: Development Environment (Compilers, Tooling, Volume Mount Target)
# ============================================================================
FROM base AS dev

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip \
    gdb \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Initialize rosdep if not already done
RUN if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then rosdep init; fi && rosdep update

# Set up development workspace
WORKDIR /workspace/object_aware_nav_ws

# Command to keep container alive for interactive attached shell
CMD ["sleep", "infinity"]

# ============================================================================
# STAGE 3: Production Build (CI/CD and Final Deployment)
# ============================================================================
FROM base AS prod

WORKDIR /workspace/object_aware_nav_ws

# Copy full source tree from host for isolated compilation
COPY ./src ./src

# Install dependencies using rosdep, build workspace, and purge source text
RUN apt-get update && \
    rosdep update && \
    rosdep install --from-paths src --ignore-src -r -y && \
    . /opt/ros/jazzy/setup.sh && \
    colcon build --merge-install --cmake-args -DCMAKE_BUILD_TYPE=Release && \
    rm -rf src/

# Default runtime entry point execution command
CMD ["ros2", "launch", "robot_sim", "robot.launch.py"]
