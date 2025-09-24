# 电网建模文件：创建IEEE 33节点模型、接入DG
import pandapower as pp
import numpy as np
from config import DG_PARAMS  # 导入DG配置参数


def create_ieee33_grid():
    """手动创建标准IEEE 33节点配电网模型（含DG）"""
    # 1. 创建空网络（移除vn_kv参数，兼容旧版本）
    net = pp.create_empty_network(name="IEEE 33节点系统", f_hz=50)
    print("✅ 开始创建IEEE 33节点模型...")

    # 2. 添加33个节点（编号0-32，明确指定电压等级12.66kV）
    for i in range(33):
        pp.create_bus(net, vn_kv=12.66, name=f"节点{i}")  # 节点电压等级单独指定
    print(f"✅ 已添加33个节点（编号0-32）")

    # 3. 添加电源（节点0为平衡节点，电压1.0p.u.）
    pp.create_ext_grid(net, bus=0, vm_pu=1.0, name="变电站电源")

    # 4. 关键修复：先定义线路标准类型（解决std_type缺失问题）
    # 定义一个自定义线路类型，包含所需的电阻、电抗等参数
    pp.create_std_type(
        net,
        name="IEEE33_line_type",  # 自定义类型名称
        data={
            "r_ohm_per_km": 0.324,  # 电阻
            "x_ohm_per_km": 0.209,  # 电抗
            "c_nf_per_km": 126.0,  # 电纳
            "max_i_ka": 0.4  # 最大电流
        },
        element="line"  # 类型为线路
    )
    print("✅ 已定义自定义线路标准类型")

    # 5. 添加32条分段线路（使用上面定义的标准类型）
    section_lines = [
        (0, 1, 0.4), (1, 2, 0.4), (2, 3, 0.6), (3, 4, 0.6), (4, 5, 0.6),
        (5, 6, 0.6), (6, 7, 0.6), (7, 8, 0.6), (8, 9, 0.6), (9, 10, 0.6),
        (10, 11, 0.6), (11, 12, 0.6), (12, 13, 0.6), (13, 14, 0.1), (14, 15, 0.1),
        (15, 16, 0.1), (16, 17, 0.1), (17, 18, 0.2), (18, 19, 0.2), (19, 20, 0.2),
        (20, 21, 0.2), (21, 22, 0.2), (22, 23, 0.2), (23, 24, 0.2), (24, 25, 0.2),
        (25, 26, 0.2), (26, 27, 0.2), (27, 28, 0.2), (28, 29, 0.2), (29, 30, 0.2),
        (30, 31, 0.2), (31, 32, 0.2)
    ]
    for idx, (from_bus, to_bus, length) in enumerate(section_lines):
        # 使用std_type参数引用自定义线路类型，移除**line_params
        pp.create_line(
            net,
            from_bus=from_bus,
            to_bus=to_bus,
            length_km=length,
            std_type="IEEE33_line_type",  # 关键：指定标准类型
            name=f"分段线路{idx + 1}"
        )
    print(f"✅ 已添加32条分段线路（初始状态：闭合）")

    # 6. 添加5条联络线路（同样使用自定义标准类型）
    contact_lines = [
        (7, 20, 0.8), (9, 14, 0.8), (12, 22, 0.8), (18, 33, 0.8), (25, 29, 0.8)
    ]
    for idx, (from_bus, to_bus, length) in enumerate(contact_lines):
        pp.create_line(
            net,
            from_bus=from_bus,
            to_bus=to_bus,
            length_km=length,
            std_type="IEEE33_line_type",  # 引用相同的线路类型
            name=f"联络线路{33 + idx}"
        )
        net.line["in_service"].iloc[-1] = False  # 联络线初始断开
    print(f"✅ 已添加5条联络线路（初始状态：断开）")

    # 7. 添加32个负荷（节点1-32）
    loads = [
        (1, 0.010, 0.006), (2, 0.009, 0.004), (3, 0.120, 0.080), (4, 0.060, 0.030),
        (5, 0.060, 0.020), (6, 0.045, 0.030), (7, 0.060, 0.035), (8, 0.060, 0.035),
        (9, 0.090, 0.040), (10, 0.090, 0.040), (11, 0.060, 0.020), (12, 0.060, 0.020),
        (13, 0.060, 0.020), (14, 0.120, 0.070), (15, 0.200, 0.100), (16, 0.100, 0.060),
        (17, 0.060, 0.030), (18, 0.060, 0.020), (19, 0.045, 0.030), (20, 0.060, 0.035),
        (21, 0.060, 0.035), (22, 0.045, 0.025), (23, 0.060, 0.030), (24, 0.060, 0.030),
        (25, 0.060, 0.030), (26, 0.045, 0.025), (27, 0.060, 0.030), (28, 0.060, 0.030),
        (29, 0.060, 0.030), (30, 0.045, 0.025), (31, 0.060, 0.030), (32, 0.060, 0.030)
    ]
    for bus, p_mw, q_mvar in loads:
        pp.create_load(net, bus=bus, p_mw=p_mw, q_mvar=q_mvar, name=f"节点{bus}负荷")
    print(f"✅ 已添加32个负荷节点")

    # 8. 接入分布式光伏（节点7和节点22）
    net.load.loc[net.load["bus"] == 7, "p_mw"] += DG_PARAMS["bus7"]["p_mw"]
    net.load.loc[net.load["bus"] == 7, "q_mvar"] += DG_PARAMS["bus7"]["q_mvar"]
    net.load.loc[net.load["bus"] == 22, "p_mw"] += DG_PARAMS["bus22"]["p_mw"]
    net.load.loc[net.load["bus"] == 22, "q_mvar"] += DG_PARAMS["bus22"]["q_mvar"]
    print(f"✅ 已接入光伏：节点7({DG_PARAMS['bus7']['p_mw']}MW)，节点22({DG_PARAMS['bus22']['p_mw']}MW)")

    # 9. 验证初始潮流计算
    try:
        pp.runpp(net, solver="nrp")  # 用牛顿-拉夫逊法，稳定性高
        initial_loss = net.res_losses["p_mw"].sum() * 1000
        print(f"✅ 初始潮流计算成功！初始网损：{initial_loss:.2f} kW")
    except Exception as e:
        print(f"❌ 初始潮流计算失败：{str(e)}")
        return None

    return net


if __name__ == "__main__":
    net = create_ieee33_grid()
