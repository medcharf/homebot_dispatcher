from setuptools import setup
import os
from glob import glob

package_name = 'homebot'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        ('share/' + package_name, ['package.xml']),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')
        ),
        (
            os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Youssef Elloumi',
    maintainer_email='youssefelloumi037@gmail.com',
    description='Minimal Language-to-Robot ROS2 proof of concept',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'task_dispatcher = homebot.task_dispatcher:main',
            'robot_simulator = homebot.robot_simulator:main',
            'sensor_node     = homebot.sensor_node:main',
        ],
    },
)
