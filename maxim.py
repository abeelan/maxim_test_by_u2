"""
@lan
"""
import logging
import time
import uiautomator2 as u2
from common.logger import Logger

# TODO：获取安装时间；获取启动时间；获取卸载时间


class Maxim:
    """通过 u2 执行 maxim
    """
    def __init__(self,
                 pkg_name,
                 run_minutes,
                 device=None,
                 throttle=500,
                 model="mix",
                 output="/sdcard/maxim_output"):
        """
        :param pkg_name: 【必填】运行 APP 的包名
        :param run_minutes: 【必填】运行时长
        :param device: 设备号，默认当前连接设备（仅一台时）
        :param throttle: 操作间隔，默认 500
        :param model: 该参数不为"troy"的情况下，都是 mix 模式
        :param output: 日志输出路径，默认 /sdcard/maxim_output
        """
        self.d = u2.connect(device)
        self.pkg_name = pkg_name
        self.run_minutes = run_minutes
        self.throttle = throttle
        self.model = model
        self.output = output

    def exec_maxim(self):
        """执行 maxim 命令
        """
        # 执行入口（固定不变）
        exec_cmd = "CLASSPATH=/sdcard/monkey.jar:/sdcard/framework.jar " \
                   "exec app_process /system/bin tv.panda.test.monkey.Monkey"

        pkg_name = f"-p {self.pkg_name}"
        run_minutes = f"--running-minutes {self.run_minutes}"  # 如果没加 --running-minutes 则代表发送事件数
        log_level = "-v -v"
        throttle = f"--throttle {self.throttle}"
        model = "--uiautomatortroy" if self.model == "troy" else "--uiautomatormix"

        """
        monkey 的相关参数参考：https://developer.android.com/studio/test/monkey
        --pct-rotation 0  # 取消旋转屏幕
        --pct-reset 0     # 关闭 APP 重启事件，默认占比 0.3%
        --pct-back 5      # 设置 BACK 占比，默认占比 10%
        """
        monkey_params = "--pct-rotation 0  --pct-reset 0"

        image_polling = "--imagepolling"  # 崩溃回溯截图，生效条件: throttle > 200 && max.takeScreenShot = true

        # 设置白名单，黑名单放置内存卡目录自动生效
        white_list = f"--act-whitelist-file /sdcard/awl.strings"

        output_dir = f"--output-directory {self.output}"

        cmd = f"{exec_cmd} {pkg_name} {monkey_params} {log_level} {throttle} {run_minutes} " \
              f"{model} {image_polling} {white_list} {output_dir}"

        logging.info(cmd.split("tv.panda.test.monkey.Monkey")[-1])

        # stream 模式，保证不会 timeout 导致杀掉，底层上是一个 requests 库提供的 streaming 模式的 response
        task = self.d.shell(cmd, stream=True)
        try:
            for line in task.iter_lines():
                logging.info(line.decode())
        finally:
            task.close()

    def start_uiautomator_server(self):
        # 重新让 atx-agent 拉活 uiautomator-server 进程，
        # 或者执行下一条需要 uiautomator-server 的命令也会自行拉活
        self.d.uiautomator.start()

    def stop_uiautomator_server(self):
        # 启动前关闭 atx-agent 守护的 uiautomator-server 进程
        self.d.uiautomator.stop()

    def setup(self):
        # 推送所有依赖到设备
        rely = ["monkey.jar", "framework.jar", "awl.strings", "max.config", "max.widget.black"]
        for j in rely:
            if not self.d.shell(f"ls sdcard | grep '{j}'").output:
                self.d.push(f"{j}", "/sdcard/")
                logging.info(f"adb push >>> sdcard/{j}")

        # 设备锁屏处理
        if not self.d.info.get('screenOn'):
            self.d.screen_on()
            self.d.swipe(0.5, 0.8, 0.5, 0.2)  # 上滑解锁

        # 删除所有历史日志
        self.d.shell("rm -rf /sdcard/maxim_output*")

    def teardown(self):
        """
        如果出现闪退，则将日志拉到 PC
        """
        if self.d.shell("ls sdcard | grep maxim_output").output:
            if self.d.shell("ls sdcard/maxim_output | grep crash").output:
                time_format = time.strftime("%y%m%d_%H_%M_%S", time.localtime())
                self.d.pull("/sdcard/maxim_output/crash-dump.log", f"../maxim_crash_{time_format}.log")
                logging.info(f"Crash Log > maxim_crash_{time_format}.log")
                logging.info(f"Crash Image > /sdcard/crash_$timestamp/")
            else:
                logging.info("No Crash，Nice.")
        else:
            logging.info("Not found maxim_output，Carried out a lonely.")
            logging.info("执行了个寂寞，咋没有输出日志呢～")

    def run(self):
        self.setup()
        self.stop_uiautomator_server()
        self.exec_maxim()
        self.start_uiautomator_server()
        self.teardown()


if __name__ == '__main__':
    Logger()
    # app = Maxim("cn.wejuan.reader", 1)
    app = Maxim("com.esbook.reader", 5)
    app.run()
