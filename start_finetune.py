import paddle
from paddlenlp.transformers import UIFinetuner
try:
    # 尝试从正确位置导入
    from paddlenlp.experimental.autonlp import UIFinetuner
except ImportError:
    try:
        from paddlenlp.transformers.uie.finetune import UIFinetuner
    except ImportError:
        # 如果还是找不到，我们直接使用 Taskflow 自带的微调逻辑入口
        print("正在尝试备选导入路径...")

# 如果上面的高级接口都失效，我们改用 paddlenlp 官方推荐的通用 Trainer
# 但为了简单起见，请先尝试这个极其简化的 UIE 训练触发器：
from paddlenlp.taskflow import Taskflow

print("正在初始化微调环境...")

# 1. 定义 Schema
schema = ['质量问题', '安全问题', '管理问题']

# 2. 这里的技巧是：UIE 并没有提供一个简单的 'UIFinetuner' 类
# 它是通过命令行脚本运行的。既然 python -m 失败了，
# 我们直接在脚本里模拟命令行调用：
import os
import sys

# 构建微调参数
args = [
    "paddlenlp.taskflow.information_extraction.finetune",
    "--device", "cpu",
    "--model_name_or_path", "uie-base",
    "--output_dir", "./my_finetuned_uie",
    "--train_path", "train.txt",
    "--dev_path", "dev.txt",
    "--max_seq_len", "512",
    "--per_device_train_batch_size", "4",
    "--learning_rate", "1e-5",
    "--num_train_epochs", "20",
    "--logging_steps", "5",
    "--save_steps", "50"
]

# 动态导入微调函数并运行
from paddlenlp.taskflow.information_extraction.finetune import do_train

# 伪造命令行参数给 do_train
import argparse
parser = argparse.ArgumentParser()
# 这里直接调用 do_train 可能会因为缺少参数解析报错
# 最稳妥的办法是：直接执行系统指令
cmd = f"/opt/anaconda3/bin/python -m paddlenlp.taskflow.information_extraction.finetune " + " ".join(args[1:])
print(f"执行指令: {cmd}")
os.system(cmd)