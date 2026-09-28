#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist

def publisher():
    # 先初始化节点，名称设为 simple_topic_publisher
    rospy.init_node('simple_topic_publisher', anonymous=True)

    # 创建 publisher，发布到 /cmd_vel，消息类型为 Twist，队列大小设为 1
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)

    # 设置发布频率为 10 Hz
    rate = rospy.Rate(10)

    while not rospy.is_shutdown():
        # 创建 Twist 消息实例
        msg = Twist()

        # 设置线速度 x 轴，前进 0.5 m/s
        msg.linear.x = 0.5

        # 设置角速度 z 轴，旋转 0.4 rad/s
        msg.angular.z = 0.4

        # 发布消息
        pub.publish(msg)

        # 打印日志
        rospy.loginfo("Publishing: linear.x=%.2f, angular.z=%.2f" % (msg.linear.x, msg.angular.z))

        # 按照 10 Hz 休眠
        rate.sleep()

if __name__ == '__main__':
    try:
        publisher()
    except rospy.ROSInterruptException:
        pass