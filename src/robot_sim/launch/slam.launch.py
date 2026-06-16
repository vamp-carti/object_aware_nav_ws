import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    parameters = [{
        'use_sim_time': True,
        'subscribe_depth': True,
        'subscribe_rgb': True,
        'subscribe_scan': True,
        'frame_id': 'base_footprint',
        'odom_frame_id': 'odom',
        'map_frame_id': 'map',
        'publish_tf': True,
        'approx_sync': True,
        'sync_queue_size': 30,
        
        'qos_image': 2,
        'qos_camera_info': 2,
        'qos_scan': 2,
        'qos_odom': 2
    }]

    remappings = [
        ('rgb/image', '/camera/image_raw'),
        ('rgb/camera_info', '/camera/camera_info'),
        ('depth/image', '/camera/depth/image_raw'),
        ('scan', '/scan'),
        ('odom', '/odom')
    ]

    rtabmap_slam_node = Node(
        package='rtabmap_slam',
        executable='rtabmap',
        output='screen',
        parameters=parameters,
        remappings=remappings,
        arguments=['-d']
    )

    return LaunchDescription([
        rtabmap_slam_node
    ])