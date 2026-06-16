import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

def generate_launch_description():
    pkg_robot_sim = get_package_share_directory('robot_sim')
    xacro_file = os.path.join(pkg_robot_sim, 'description', 'robot.urdf.xacro')
    
    # Declare the launch argument explicitly so it catches the 'true' string from sim.launch.py
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    # Map the launch argument to a live configuration tracking object
    use_sim_time_config = LaunchConfiguration('use_sim_time')

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': Command(['xacro ', xacro_file]),
            'use_sim_time': use_sim_time_config # <-- Explicitly bind to the configuration object
        }]
    )

    return LaunchDescription([
        use_sim_time_arg,
        robot_state_publisher_node
    ])