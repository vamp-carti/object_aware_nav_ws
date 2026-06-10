import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_robot_sim = get_package_share_directory('robot_sim')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # 1. Include the Robot State Publisher Launch file
    robot_state_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_robot_sim, 'launch', 'robot_state_publisher.launch.py')
        )
    )

    # 2. Locate world configuration file
    world_file_path = os.path.join(pkg_robot_sim, 'worlds', 'empty_world.sdf')

    # 3. Include native Gazebo simulation engine
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file_path}'}.items()
    )

    # 4. Spawner Node to inject the URDF model into Gazebo
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'object_aware_robot',
            '-z', '0.1'
        ]
    )

    return LaunchDescription([
        robot_state_publisher,
        gazebo,
        spawn_robot
    ])
