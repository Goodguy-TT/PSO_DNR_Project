import pandapower as pp
from pandapower.topology import create_nxgraph
from networkx import has_path
from config import CONTACT_SWITCH_IDX  # 导入联络开关索引

def calculate_loss(net, code):
    """
    根据编码（开关状态）计算网损
    参数：
        net：pandapower电网对象
        code：二进制编码（列表，如[0,1,0,0,0]）
    返回：
        loss_kW：网损（kW），潮流不收敛返回10000（惩罚）
    """
    # 1. 按编码更新联络开关状态
    for i in range(len(code)):
        switch_idx = CONTACT_SWITCH_IDX[i]
        net.line["in_service"][switch_idx] = (code[i] == 1)  # 1=闭合，0=断开

    # 2. 运行潮流计算
    try:
        pp.runpp(net, solver="bfsw")
        loss_kW = net.res_losses["p_mw"].sum() * 1000  # MW→kW
    except:
        loss_kW = 10000  # 潮流不收敛，返回极大值（惩罚）

    return loss_kW

def check_topology(net, code):
    """
    校验拓扑合法性：无环+无孤岛
    参数：
        net：pandapower电网对象
        code：二进制编码
    返回：
        is_valid：布尔值（True=合法，False=非法）
    """
    # 1. 按编码更新开关状态
    for i in range(len(code)):
        switch_idx = CONTACT_SWITCH_IDX[i]
        net.line["in_service"][switch_idx] = (code[i] == 1)

    # 2. 构建拓扑图
    G = create_nxgraph(net, include_lines=True, include_switches=True)

    # 3. 校验无孤岛：所有节点是否与电源点（0）连通
    all_connected = True
    for bus in net.bus.index:
        if not has_path(G, 0, bus):
            all_connected = False
            break

    # 4. 校验无环：有效支路数 = 节点数 - 1（树状结构）
    valid_lines = len(net.line[net.line["in_service"] == True])
    node_count = len(net.bus)
    no_cycle = (valid_lines == node_count - 1)

    return all_connected and no_cycle

def repair_code(code):
    """
    修复非法编码：确保仅闭合1个联络开关（避免环网）
    参数：code：二进制编码
    返回：修复后的编码
    """
    close_count = sum(code)
    if close_count == 0:
        # 全断开：随机闭合1个
        rand_pos = int(np.random.randint(0, len(code), size=1))
        code[rand_pos] = 1
    elif close_count > 1:
        # 闭合过多：仅保留1个
        code = [0] * len(code)
        rand_pos = int(np.random.randint(0, len(code), size=1))
        code[rand_pos] = 1
    return code

# 测试：运行此文件可验证工具函数
if __name__ == "__main__":
    import numpy as np
    from grid_model import create_ieee33_grid

    # 加载电网模型
    net = create_ieee33_grid()
    if net is None:
        exit()

    # 测试网损计算
    test_code = [0,1,0,0,0]  # 闭合第2个联络开关
    loss = calculate_loss(net, test_code)
    print(f"测试编码{test_code}的网损：{loss:.2f} kW")

    # 测试拓扑校验
    is_valid = check_topology(net, test_code)
    print(f"拓扑合法性：{'合法' if is_valid else '非法'}")