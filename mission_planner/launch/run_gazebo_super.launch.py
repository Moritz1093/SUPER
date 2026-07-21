import os.path
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Wir nutzen RViz aus dem super_planner oder mission_planner Paket
    package_path = get_package_share_directory('super_planner')
    
    default_config_path = 'waypoint.yaml'
    default_data_path = 'benchmark.txt'
    super_config_name = 'static_dense.yaml'

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time', default_value='true', # Auf TRUE setzen für Gazebo Clock!
        description='Use simulation (Gazebo) clock if true'
    )

    ld = LaunchDescription()
    ld.add_action(declare_use_sim_time_cmd)

    # 1. Mission Planner (Wegpunkt-Schnittstelle)
    mission_planner = Node(
        package='mission_planner',
        executable='waypoint_mission',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'config_name': default_config_path,
            'data_name': default_data_path
        }]
    )
    ld.add_action(mission_planner)

    # 2. SUPER Planner (Kern-Algorithmus)
    # Remapping sorgt dafür, dass SUPER die echten Gazebo-/PX4-Topics liest
    super_planner_node = Node(
        package='super_planner',
        executable='fsm_node',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'config_name': super_config_name,
        }],
        remappings=[
            # ('ALTER_TOPIC_IN_SUPER', 'UNSER_GAZEBO_TOPIC')
            ('/odom_world', '/fmu/out/vehicle_odometry'),
            ('/cloud_in', '/livox/lidar_sim')
        ]
    )
    ld.add_action(super_planner_node)

    # 3. RViz2 zur Visualisierung
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen'
    )
    ld.add_action(rviz_node)

    return ld
