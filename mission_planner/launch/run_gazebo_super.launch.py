import os.path
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    package_path = get_package_share_directory('super_planner')
    
    default_config_path = 'waypoint.yaml'
    default_data_path = 'benchmark.txt'
    super_config_name = 'static_dense.yaml'

    use_sim_time = LaunchConfiguration('use_sim_time')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    ld = LaunchDescription()
    ld.add_action(declare_use_sim_time_cmd)

    # 1. Mission Planner
    mission_planner = Node(
        package='mission_planner',
        executable='waypoint_mission',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'config_name': default_config_path,
            'data_name': default_data_path
        }]
    )
    ld.add_action(mission_planner)

    # 2. SUPER Planner
    super_planner_node = Node(
        package='super_planner',
        executable='fsm_node',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'config_name': super_config_name,
        }],
        remappings=[
            ('/cloud_registered', '/cloud_registered'),
            ('/lidar_slam/odom', '/Odometry'),
            ('/fmu/out/vehicle_odometry', '/Odometry')
        ]
    )
    ld.add_action(super_planner_node)

    # 3. RViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )
    ld.add_action(rviz_node)

    return ld
