import numpy as np
from config import POP_SIZE, MAX_ITER, W_INIT, W_FINAL, C1, C2
from utils import calculate_loss, repair_code  # 导入工具函数

def pso_dnr(net):
    """
    基于PSO的配电网重构
    参数：net：pandapower电网对象
    返回：
        best_code：最优编码（开关状态）
        best_loss：最优网损（kW）
        iter_records：迭代过程网损记录（用于绘图）
    """
    code_len = len(CONTACT_SWITCH_IDX)  # 编码长度=联络开关数量
    iter_records = []  # 记录每代最优网损

    # 1. 初始化种群（粒子=编码）
    population = np.random.randint(0, 2, (POP_SIZE, code_len))
    # 修复初始种群中的非法编码
    for i in range(POP_SIZE):
        population[i] = repair_code(population[i].tolist())
    population = population.astype(int)

    # 2. 计算初始适应度（网损）
    fitness = np.array([calculate_loss(net, code.tolist()) for code in population])

    # 3. 初始化个体最优和全局最优
    pbest_code = population.copy()  # 个体最优编码
    pbest_fitness = fitness.copy()  # 个体最优适应度
    gbest_idx = np.argmin(fitness)  # 全局最优索引（网损最小）
    gbest_code = population[gbest_idx].copy()
    gbest_fitness = fitness[gbest_idx]

    # 记录初始全局最优
    iter_records.append(gbest_fitness)
    print(f"初始化完成，初始最优网损：{gbest_fitness:.2f} kW")

    # 4. 迭代优化
    for iter_num in range(MAX_ITER):
        # 动态调整惯性权重（线性递减）
        w = W_INIT - (W_INIT - W_FINAL) * iter_num / MAX_ITER

        for i in range(POP_SIZE):
            # a. 计算速度（离散PSO：速度是概率变化量）
            r1 = np.random.random(code_len)
            r2 = np.random.random(code_len)
            velocity = w * np.random.random(code_len) + \
                       C1 * r1 * (pbest_code[i] - population[i]) + \
                       C2 * r2 * (gbest_code - population[i])

            # b. 更新位置（Sigmoid函数离散化）
            population[i] = (1 / (1 + np.exp(-velocity))) > 0.5
            population[i] = population[i].astype(int)

            # c. 修复非法编码
            population[i] = repair_code(population[i].tolist())

            # d. 计算新适应度
            new_fitness = calculate_loss(net, population[i].tolist())

            # e. 更新个体最优
            if new_fitness < pbest_fitness[i]:
                pbest_code[i] = population[i].copy()
                pbest_fitness[i] = new_fitness

            # f. 更新全局最优
            if new_fitness < gbest_fitness:
                gbest_code = population[i].copy()
                gbest_fitness = new_fitness

        # 记录当前迭代的全局最优
        iter_records.append(gbest_fitness)
        if (iter_num + 1) % 10 == 0:  # 每10代打印一次
            print(f"迭代第{iter_num+1}次，当前最优网损：{gbest_fitness:.2f} kW")

    return gbest_code.tolist(), gbest_fitness, iter_records

# 测试：运行此文件可验证PSO算法
if __name__ == "__main__":
    from grid_model import create_ieee33_grid

    net = create_ieee33_grid()
    if net is None:
        exit()

    # 运行PSO
    best_code, best_loss, records = pso_dnr(net)
    print(f"\nPSO算法结束，最优编码：{best_code}，最优网损：{best_loss:.2f} kW")