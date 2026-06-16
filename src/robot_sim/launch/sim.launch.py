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
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # 2. Define the Gazebo world file path
    world_file_path = os.path.join(
        get_package_share_directory('robot_sim'),
        'worlds',
        'warehouse.sdf'
    )

    # 3. Include native Gazebo simulation engine with explicit environment inheritance
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': f'-r -s {world_file_path}'
        }.items()
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

    # 5. Parameter Bridge configured for flat native Gazebo topics
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'lazy': False
        }],
        arguments=[
            # 1. System Clock
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            
            # 2. Scoped Dynamic Transforms
            '/model/object_aware_robot/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            
            # 3. Odometry Position Data
            '/model/object_aware_robot/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            
            # 4. Actuator Command Control Loop
            '/cmd_vel@geometry_msgs/msg/Twist[gz.msgs.Twist',
            
            # 5. 2D Lidar Scan Stream
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            
            # 6. RGB Camera Image Matrix
            '/camera/image@sensor_msgs/msg/Image[gz.msgs.Image',
            
            # 7. Depth Camera Matrix
            '/camera/depth_image@sensor_msgs/msg/Image[gz.msgs.Image',
            
            # 8. Camera Calibration Info
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            
            # 9. Inertial Measurement Unit (IMU)
            '/world/warehouse/model/object_aware_robot/link/base_link/sensor/generic_imu/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU'
        
            # 10. Joint states (wheels)
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model' 
        ],
        remappings=[
            ('/model/object_aware_robot/tf', '/tf'),
            ('/model/object_aware_robot/odometry', '/odom'),
            ('/camera/image', '/camera/image_raw'),
            ('/camera/depth_image', '/camera/depth/image_raw'),
            
            # Explicitly force Gazebo sensor headers to match the URDF links
            ('/scan/frame_id', 'laser_frame'),
            ('/camera/image/frame_id', 'camera_link'),
            ('/camera/depth_image/frame_id', 'camera_link')
        ]
    )

    return LaunchDescription([
        robot_state_publisher,
        gazebo,
        spawn_robot,
        bridge,
    ])