import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

def generate_launch_description():
    # Locate package paths
    pkg_robot_sim = get_package_share_directory('robot_sim')
    
    # Path to the core URDF/Xacro file
    xacro_file = os.path.join(pkg_robot_sim, 'description', 'robot.urdf.xacro')
    
    # Configure the robot_state_publisher node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': Command(['xacro ', xacro_file])
        }]
    )

    return LaunchDescription([
        robot_state_publisher_node
    ])
