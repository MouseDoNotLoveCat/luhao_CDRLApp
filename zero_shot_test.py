import paddle
from paddlenlp import Taskflow
from pprint import pprint

# # 1. 开启 M1 加速
# paddle.set_device('cpu')

# # 2. 定义分类 Schema
# # 这里的标签可以随时增减，模型会自动理解语义
# schema = ['质量问题', '安全问题', '管理问题']

# # 3. 初始化 Taskflow (首次运行会自动下载模型)
# # model可选：'uie-base'(推荐), 'uie-medium', 'uie-mini'
# ie = Taskflow("information_extraction", schema=schema, model="uie-base")

# # 4. 批量测试样本
# samples = [
#     "隧道左线K12+300处发现二衬开裂。",
#     "施工现场工人未佩戴安全帽。",
#     "消火栓水压报警系统失灵。"
# ]

# # 5. 执行预测并打印结果
# results = ie(samples)

# print("\n" + "="*30)
# print("开始分类结果展示：")
# print("="*30)

# for text, res in zip(samples, results):
#     print(f"文本: {text}")
    
#     # 核心修正：UIE 的 res 应该是个字典，key 是你 schema 里的分类名
#     # 或者是列表（取决于 schema 的写法）。我们用最通用的逻辑：
#     if isinstance(res, dict) and len(res) > 0:
#         # 获取字典里的第一个分类结果
#         first_category = list(res.keys())[0]
#         details = res[first_category][0]
#         print(f"预测分类: {first_category} (置信度: {details['probability']:.4f})")
#     elif isinstance(res, list) and len(res) > 0:
#         # 如果返回的是列表格式
#         best_res = res[0]
#         # UIE 有时把标签放在 'text' 里，有时放在 'label' 里
#         label = best_res.get('text', best_res.get('label', '未知'))
#         score = best_res.get('probability', best_res.get('score', 0))
#         print(f"预测结果: {label} (置信度: {score:.4f})")
#     else:
#         print("预测结果: 无匹配 (模型不确定或未找到对应类别)")
    
#     print("-" * 30)

import json

# 1. 你提供的数据 + 我为你补充的数据
raw_data = [
    {"content": "隧道左线K12+300处发现二衬开裂。", "label": "质量问题"},
    {"content": "施工现场工人未佩戴安全帽。", "label": "安全问题"},
    {"content": "消火栓水压报警系统失灵。", "label": "安全问题"},
    {"content": "项目部安全穿透式管理不到位。", "label": "管理问题"},
    # --- 为你拟定的补充/测试数据 ---
    {"content": "桥梁墩身混凝土表面出现蜂窝麻面。", "label": "质量问题"},
    {"content": "深基坑开挖未按规定设置临边防护栏杆。", "label": "安全问题"},
    {"content": "现场施工日志记录不完整，签字手续缺失。", "label": "管理问题"},
    {"content": "预制梁场张拉记录数据异常，涉嫌造假。", "label": "质量问题"},
    {"content": "临时用电电缆直接拖地，未架空处理。", "label": "安全问题"}
]

def convert_to_uie_format(data, save_path):
    with open(save_path, 'w', encoding='utf-8') as f:
        for item in data:
            # UIE 分类任务的特定格式：prompt 就是分类名
            record = {
                "content": item["content"],
                "result_list": [],
                "prompt": item["label"]
            }
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

# 生成训练集
convert_to_uie_format(raw_data, 'train.txt')
# 演示起见，暂用同样数据作为验证集
convert_to_uie_format(raw_data, 'dev.txt')

print("✅ 成功生成 train.txt 和 dev.txt，可以开始微调了。")