# rob_example

ROS 1 (Noetic) 软件包：创建一个 Publisher 节点，以 10 Hz 向 `/cmd_vel` 发布 `geometry_msgs/Twist` 消息，驱动差速驱动机器人移动。

本包是 ROS 练习 **「创建第一个 Publisher」** 的完成结果。

## 目录

- [功能简介](#功能简介)
- [环境要求](#环境要求)
- [目录结构](#目录结构)
- [关键文件](#关键文件)
- [安装与编译](#安装与编译)
- [使用方法](#使用方法)
- [验证](#验证)
- [运动参数速查](#运动参数速查)
- [常见问题](#常见问题)
- [关键概念](#关键概念)

## 功能简介

- 创建 ROS 节点 `simple_topic_publisher`
- 以 10 Hz 频率向 `/cmd_vel` 发布 `geometry_msgs/Twist` 消息
- 让差速驱动机器人（Turtlebot 2 / Kobuki 等）以指定线速度、角速度移动

默认运动：前进 `0.5 m/s`，同时左转 `0.4 rad/s`，即走圆弧。

## 环境要求

| 项目 | 版本 |
|---|---|
| 操作系统 | Ubuntu 20.04 |
| ROS | ROS 1 Noetic |
| Python | Python 3 |
| 依赖 | `rospy`、`geometry_msgs` |

仿真环境需要 Gazebo 与 Turtlebot 相关包（如 `turtlebot_gazebo`）。

## 目录结构

```
rob_example/
├── CMakeLists.txt
├── package.xml
├── README.md
├── .gitignore
├── launch/
│   └── robot_example.launch
└── scripts/
    └── rob_example.py
```

## 关键文件

### scripts/rob_example.py

发布者节点脚本：

```python
#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist

def publisher():
    # 初始化节点，anonymous=True 防止重名
    rospy.init_node('simple_topic_publisher', anonymous=True)

    # 创建 Publisher：话题 /cmd_vel，类型 Twist，队列长度 1
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)

    # 发布频率 10 Hz
    rate = rospy.Rate(10)

    while not rospy.is_shutdown():
        msg = Twist()

        # 线速度 x 轴：前进 0.5 m/s
        msg.linear.x = 0.5
        # 角速度 z 轴：左转 0.4 rad/s
        msg.angular.z = 0.4

        pub.publish(msg)
        rospy.loginfo("Publishing: linear.x=%.2f, angular.z=%.2f"
                      % (msg.linear.x, msg.angular.z))
        rate.sleep()

if __name__ == '__main__':
    try:
        publisher()
    except rospy.ROSInterruptException:
        pass
```

关键点：

- `queue_size=1`：速度指令只保留最新一条，避免积压
- `rate=10`：10 Hz 发布，运动平滑
- `linear.x=0.5`、`angular.z=0.4`：前进同时左转，走圆弧

### launch/robot_example.launch

```xml
<launch>
    <node pkg="rob_example"
          type="rob_example.py"
          name="simple_topic_publisher"
          output="screen"/>
</launch>
```

- `type` 必须与 `scripts/` 下的文件名一致
- `output="screen"`：日志输出到终端

### CMakeLists.txt（关键片段）

```cmake
catkin_install_python(PROGRAMS
  scripts/rob_example.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
```

作用：把 Python 脚本安装到 devel 空间，让 `rosrun` / `roslaunch` 能找到并执行。

## 安装与编译

```bash
# 1. 将包放入 catkin 工作空间 src 目录
cp -r rob_example ~/catkin_ws/src/

# 2. 编译
cd ~/catkin_ws
catkin_make

# 3. source 环境
source devel/setup.bash
```

可把 source 写入 `~/.bashrc`：

```bash
echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

## 使用方法

1. 启动机器人仿真：

```bash
roslaunch turtlebot_gazebo turtlebot_world.launch
```

2. 确认 `/cmd_vel` 有订阅者：

```bash
rostopic info /cmd_vel
```

`Subscribers:` 下应能看到 `/gazebo` 或驱动节点。

3. 启动发布者：

```bash
roslaunch rob_example robot_example.launch
```

终端持续输出：

```
[INFO] [...]: Publishing: linear.x=0.50, angular.z=0.40
```

Gazebo 中的机器人开始走圆弧。

4. 停止：在 roslaunch 终端按 `Ctrl+C`。

## 验证

| 命令 | 用途 | 期望结果 |
|---|---|---|
| `rostopic info /cmd_vel` | 查看话题信息 | Type 为 `geometry_msgs/Twist` |
| `rostopic echo /cmd_vel` | 查看消息内容 | `linear.x: 0.5`，`angular.z: 0.4` |
| `rostopic hz /cmd_vel` | 查看发布频率 | `average rate: 10.000` |
| `rosnode list` | 查看节点 | 包含 `/simple_topic_publisher` |
| `rosmsg show geometry_msgs/Twist` | 查看消息结构 | 显示 linear / angular 两个 Vector3 |
| `rospack find rob_example` | 查找包路径 | 显示包所在绝对路径 |

## 运动参数速查

| 运动方式 | linear.x | angular.z |
|---|---|---|
| 直行前进 | 0.5 | 0.0 |
| 原地左转 | 0.0 | 0.5 |
| 原地右转 | 0.0 | -0.5 |
| 圆弧前进（左转） | 0.5 | 0.4 |
| 圆弧前进（右转） | 0.5 | -0.4 |
| 停止 | 0.0 | 0.0 |

单位：`linear.x` 为 m/s，建议 0～1；`angular.z` 为 rad/s，建议 0～1。

## 常见问题

1. **`ros2: command not found`** —— 本包是 ROS 1，应使用 `rostopic`、`rosmsg`、`roslaunch` 等命令，而不是 `ros2 topic`、`ros2 interface`。

2. **`RLException: [xxx.launch] is neither a launch file in package ...`** —— 检查包名（`rospack find rob_example`）、launch 文件是否在 `launch/` 目录、文件名拼写。

3. **日志刷屏** —— 正常，发布者在 while 循环中持续发布。`Ctrl+C` 停止。

4. **机器人不动** —— 依次检查：
   - `rostopic info /cmd_vel` 的 Subscribers 是否有 `/gazebo` 或驱动节点
   - Gazebo 仿真时间是否在推进（非暂停）
   - 速度是否太小，可改 `linear.x = 1.0`
   - 若机器人订阅的不是 `/cmd_vel`，用 `rostopic list` 找到实际话题并 remap：

```xml
<node pkg="rob_example" type="rob_example.py" name="simple_topic_publisher" output="screen">
    <remap from="/cmd_vel" to="/实际话题名"/>
</node>
```

5. **编译后 roslaunch 找不到节点** —— 确认 CMakeLists.txt 已添加 `catkin_install_python`，重新 `catkin_make`，并 `source devel/setup.bash`。

## 关键概念

| 概念 | 说明 |
|---|---|
| 节点 Node | ROS 中的可执行单元 |
| 发布者 Publisher | 向话题发送消息的节点 |
| 订阅者 Subscriber | 从话题接收消息的节点 |
| 话题 Topic | 消息传输通道，如 `/cmd_vel` |
| 消息 Message | 话题上的数据，如 `geometry_msgs/Twist` |
| Twist | 速度消息，含 linear（线速度）、angular（角速度） |
| 差速驱动 | 只能沿 x 轴直行、绕 z 轴旋转，只用 linear.x 与 angular.z |
| catkin 工作空间 | ROS 1 代码组织方式，`src/` 放源码，`devel/` 放编译产物 |

## 参考

- ROS Wiki: http://wiki.ros.org/
- geometry_msgs/Twist: http://docs.ros.org/en/noetic/api/geometry_msgs/html/msg/Twist.html
- rospy: http://wiki.ros.org/rospy

## License

本项目采用 [MIT License](./LICENSE)。
