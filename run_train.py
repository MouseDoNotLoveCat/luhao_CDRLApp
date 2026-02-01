import paddle
from paddlenlp.trainer import PdArgumentParser, TrainingArguments
from paddlenlp.datasets import load_dataset
from paddlenlp.transformers import UIEModel, ErnieTokenizer
from paddlenlp.data import DataCollatorWithPadding

# 1. 强制设置设备
paddle.set_device('cpu')

# 2. 模拟微调所需的最小化配置
class UIEDataCollator(DataCollatorWithPadding):
    def __call__(self, examples):
        return super().__call__(examples)

def train():
    # 初始化模型和分词器
    model_name = "uie-base"
    tokenizer = ErnieTokenizer.from_pretrained(model_name)
    model = UIEModel.from_pretrained(model_name)

    # 这里的关键是：直接手动指定训练参数，不再依赖命令行
    training_args = TrainingArguments(
        output_dir="./my_finetuned_uie",
        per_device_train_batch_size=4,
        learning_rate=1e-5,
        num_train_epochs=20,
        logging_steps=5,
        save_steps=50,
        do_train=True,
        device="cpu"
    )

    # 注意：这里需要 paddlenlp 官方提供的 UIE 训练逻辑
    # 如果上面的 UIEModel 无法直接 train，最简单的办法是使用 Taskflow 的微调入口
    # 我们尝试用最原始的 Taskflow 封装运行
    print("🚀 环境对齐成功，准备开始微调...")
    
    # 由于 2.6.1 版本限制，我们直接调用内置的 trainer 逻辑
    from paddlenlp.taskflow.information_extraction.finetune import do_train
    
    # 构造一个符合要求的参数对象
    from types import SimpleNamespace
    custom_args = SimpleNamespace(
        device="cpu",
        model_name_or_path="uie-base",
        output_dir="./my_finetuned_uie",
        train_path="train.txt",
        dev_path="dev.txt",
        max_seq_len=512,
        per_device_train_batch_size=4,
        learning_rate=1e-5,
        num_train_epochs=20,
        logging_steps=5,
        save_steps=50,
        seed=42
    )
    
    do_train(custom_args)

if __name__ == "__main__":
    train()