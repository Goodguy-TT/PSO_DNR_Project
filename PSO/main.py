import os
from config import CONTACT_SWITCH_IDX, SAVE_RESULTS, RESULT_PATH
from grid_model import create_ieee33_grid
from pso_algorithm import pso_dnr
from visualization import plot_loss_curve, plot_voltage_distribution

def main():
    print("="*50)
    print("          基于PSO的配电网重构实验（含DG场景）          ")
    print("="*50)

    # 1. 步骤1：创建电网模型（含DG）
    print("\n【步骤1/4】创建配电网模型...")
    net = create_ieee33_grid()
    if net is None:
        print("❌ 电网模型创建失败，实验终止")
        return

    # 2. 步骤2：运行PSO算法重构
    print("\n【步骤2/4】运行PSO算法...")
    best_code, best_loss, iter_records = pso_dnr(net)

    # 3. 步骤3：结果可视化
    print("\n【步骤3/4】绘制结果图表...")
    plot_loss_curve(iter_records)  # 网损迭代曲线
    plot_voltage_distribution(net, best_code, CONTACT_SWITCH_IDX)  # 电压分布

    # 4. 步骤4：输出最终结果
    print("\n【步骤4/4】输出实验总结...")
    print("\n" + "="*50)
    print("                    实验结果总结                    ")
    print("="*50)
    print(f"最优联络开关编码：{best_code}")
    print(f"编码含义：0=断开，1=闭合（对应联络开关33-37）")
    print(f"重构后最优网损：{best_loss:.2f} kW")

    # 计算初始网损（用于对比）
    initial_code = [0]*len(CONTACT_SWITCH_IDX)  # 初始状态：所有联络开关断开
    from utils import calculate_loss
    initial_loss = calculate_loss(net, initial_code)
    print(f"重构前初始网损：{initial_loss:.2f} kW")
    print(f"网损降低率：{((initial_loss - best_loss)/initial_loss)*100:.2f}%")

    # 输出开关操作指令
    print("\n【工程操作建议】")
    for i in range(len(best_code)):
        switch_num = 33 + i  # 编码0对应物理开关33
        status = "闭合" if best_code[i] == 1 else "断开"
        print(f"联络开关{switch_num}：{status}")
    print("="*50)

    # 保存结果日志（可选）
    if SAVE_RESULTS:
        os.makedirs(RESULT_PATH, exist_ok=True)
        log_path = os.path.join(RESULT_PATH, "实验日志.txt")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("实验结果总结\n")
            f.write(f"最优编码：{best_code}\n")
            f.write(f"初始网损：{initial_loss:.2f} kW\n")
            f.write(f"最优网损：{best_loss:.2f} kW\n")
            f.write(f"网损降低率：{((initial_loss - best_loss)/initial_loss)*100:.2f}%\n")
        print(f"\n📝 实验日志已保存至：{log_path}")

if __name__ == "__main__":
    main()