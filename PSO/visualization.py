import matplotlib.pyplot as plt
import os
from config import RESULT_PATH, SAVE_RESULTS

# 设置中文字体（避免乱码）
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def plot_loss_curve(iter_records):
    """
    绘制网损迭代曲线
    参数：iter_records：迭代过程网损记录
    """
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(iter_records)), iter_records, "b-o", linewidth=2, markersize=4)
    plt.xlabel("迭代次数", fontsize=12)
    plt.ylabel("网损（kW）", fontsize=12)
    plt.title("PSO算法网损迭代曲线", fontsize=14, pad=20)
    plt.grid(True, alpha=0.3)

    # 保存图片（如果配置开启）
    if SAVE_RESULTS:
        os.makedirs(RESULT_PATH, exist_ok=True)  # 创建结果文件夹
        save_path = os.path.join(RESULT_PATH, "网损迭代曲线.png")
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"📊 网损曲线已保存至：{save_path}")
    plt.show()

def plot_voltage_distribution(net, best_code, contact_switch_idx):
    """
    绘制重构后的节点电压分布
    参数：
        net：电网对象
        best_code：最优编码
        contact_switch_idx：联络开关索引
    """
    # 先按最优编码更新开关状态
    for i in range(len(best_code)):
        switch_idx = contact_switch_idx[i]
        net.line["in_service"][switch_idx] = (best_code[i] == 1)
    pp.runpp(net)  # 重新计算潮流

    # 绘图
    plt.figure(figsize=(12, 6))
    bus_nums = net.bus.index  # 节点编号
    voltages = net.res_bus["vm_pu"]  # 节点电压（p.u.）

    plt.plot(bus_nums, voltages, "r-o", linewidth=2, markersize=4, label="重构后电压")
    plt.axhline(y=0.95, color="green", linestyle="--", linewidth=1.5, label="电压下限0.95p.u.")
    plt.axhline(y=1.05, color="red", linestyle="--", linewidth=1.5, label="电压上限1.05p.u.")

    plt.xlabel("节点编号", fontsize=12)
    plt.ylabel("节点电压（标幺值p.u.）", fontsize=12)
    plt.title("重构后节点电压分布", fontsize=14, pad=20)
    plt.legend(loc="best")
    plt.grid(True, alpha=0.3)

    # 保存图片
    if SAVE_RESULTS:
        os.makedirs(RESULT_PATH, exist_ok=True)
        save_path = os.path.join(RESULT_PATH, "节点电压分布.png")
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"📊 电压分布已保存至：{save_path}")
    plt.show()