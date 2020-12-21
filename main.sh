# Usage： 
# 	运行10分钟
# 	./main.sh 10

monkey="monkey.jar"
framework="framework.jar"


monkey_jar=`adb shell ls sdcard | grep "$monkey"`
framework_jar=`adb shell ls sdcard | grep "$framework"`


# 判断是否存在 monkey.jar 
if [ ! -f "$monkey_jar" ]; then
	echo adb push "$monkey" /sdcard
else
	echo "monkey.jar is existing."
fi

# 判读是否存在 framework.jar
if [ ! -f "$framework_jar" ]; then
	echo adb push "$framework" /sdcard
else
	echo "framework.jar is existing."
fi

# 将配置文件推送至设备
adb push "max.widget.black" /sdcard
adb push "awl.strings" /sdcard
adb push "max.config" /sdcard

sleep 1

# 删除历史文件
adb shell rm -rf /sdcard/maxim_output

# maxim 运行命令
 adb shell CLASSPATH=/sdcard/monkey.jar:/sdcard/framework.jar exec app_process /system/bin tv.panda.test.monkey.Monkey -p com.esbook.reader --pct-rotation 0 --running-minutes $1 -v -v --throttle 500 --uiautomatormix -v -v --output-directory /sdcard/maxim_output



# 判断执行成功，以上一条命令执行完的状态码为判断条件
if [ $? -eq 0 ]; then
	time=$(date ""+%Y%m%d_%H%M%S"")
	echo "日志目录:"$time""
	adb pull /sdcard/maxim_log/ ./"$time"
	sleep 1
	echo ">>> 执行完毕 <<<"
else
	echo ">>> 异常分支，执行完毕 <<<"
fi


