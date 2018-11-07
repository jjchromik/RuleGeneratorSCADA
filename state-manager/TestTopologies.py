#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This file contains functions for hard coded topologies.
'''
from GridComponents.AbstractComponent import getAllComponentsOfType
from GridComponents.Bus import Bus
from GridComponents.Consumer import Consumer
from GridComponents.DynamicInterlock import DynamicInterlock
from GridComponents.Fuse import Fuse
from GridComponents.Generator import Generator
from GridComponents.LocalRTU import LocalRTU
from GridComponents.Meter import Meter
from GridComponents.PowerLine import PowerLine
from GridComponents.ProtectiveRelay import ProtectiveRelay
from GridComponents.StaticInterlock import StaticInterlock
from GridComponents.Switch import Switch
from GridComponents.Transformer import Transformer


def initiateTopologyAlpha():
    """
    Initialize Alpha topology.
    :return: Alpha topology
    """
    sw10 = Switch("rtu_global_sw10")
    sw20 = Switch("rtu_global_sw20")
    sw11 = Switch("rtu_global_sw11")
    sw21 = Switch("rtu_global_sw21")
    sw31 = Switch("rtu_global_sw31")
    sw41 = Switch("rtu_global_sw41")
    sw51 = Switch("rtu_global_sw51")
    sw32 = Switch("rtu_global_sw32")
    sw42 = Switch("rtu_global_sw42")
    sw52 = Switch("rtu_global_sw52")
    sw62 = Switch("rtu_global_sw62")
    sw72 = Switch("rtu_global_sw72")
    sw82 = Switch("rtu_global_sw82")
    sw92 = Switch("rtu_global_sw92")
    sw63 = Switch("rtu_global_sw63")
    sw73 = Switch("rtu_global_sw73")
    sw83 = Switch("rtu_global_sw83")
    sw93 = Switch("rtu_global_sw93")
    m10 = Meter("rtu_global_m10")
    m20 = Meter("rtu_global_m20")
    m11 = Meter("rtu_global_m11")
    m21 = Meter("rtu_global_m21")
    m31 = Meter("rtu_global_m31")
    m41 = Meter("rtu_global_m41")
    m51 = Meter("rtu_global_m51")
    m32 = Meter("rtu_global_m32")
    m42 = Meter("rtu_global_m42")
    m52 = Meter("rtu_global_m52")
    m62 = Meter("rtu_global_m62")
    m72 = Meter("rtu_global_m72")
    m82 = Meter("rtu_global_m82")
    m92 = Meter("rtu_global_m92")
    m63 = Meter("rtu_global_m63")
    m73 = Meter("rtu_global_m73")
    m83 = Meter("rtu_global_m83")
    m93 = Meter("rtu_global_m93")
    l1 = PowerLine("rtu_global_l1", 0.8, startSwitch=sw10, endSwitch=sw11, startMeter=m10, endMeter=m11)
    l2 = PowerLine("rtu_global_l2", 0.5, startSwitch=sw20, endSwitch=sw21, startMeter=m20, endMeter=m21)
    l3 = PowerLine("rtu_global_l3", 0.3, startSwitch=sw31, endSwitch=sw32, startMeter=m31, endMeter=m32)
    l4 = PowerLine("rtu_global_l4", 0.4, startSwitch=sw41, endSwitch=sw42, startMeter=m41, endMeter=m42)
    l5 = PowerLine("rtu_global_l5", 0.5, startSwitch=sw51, endSwitch=sw52, startMeter=m51, endMeter=m52)
    l6 = PowerLine("rtu_global_l6", 0.3, startSwitch=sw62, endSwitch=sw63, startMeter=m62, endMeter=m63)
    l7 = PowerLine("rtu_global_l7", 0.5, startSwitch=sw72, endSwitch=sw73, startMeter=m72, endMeter=m73)
    l8 = PowerLine("rtu_global_l8", 0.3, startSwitch=sw82, endSwitch=sw83, startMeter=m82, endMeter=m83)
    l9 = PowerLine("rtu_global_l9", 0.3, startSwitch=sw92, endSwitch=sw93, startMeter=m92, endMeter=m93)
    g1 = Generator("rtu_global_g1", [], [l1])
    g2 = Generator("rtu_global_g2", [], [l2])
    c1 = Consumer("rtu_global_c1", [l6], [])
    c2 = Consumer("rtu_global_c2", [l7], [])
    c3 = Consumer("rtu_global_c3", [l8], [])
    c4 = Consumer("rtu_global_c4", [l9], [])
    bus1 = Bus("rtu_global_b1", [l1, l2], [l3, l4, l5])
    bus2 = Bus("rtu_global_b2", [l3, l4, l5], [l6, l7, l8, l9])
    rtu1 = LocalRTU("rtu1", [bus1])
    rtu2 = LocalRTU("rtu2", [bus2])
    rtu3 = LocalRTU("rtuGenerators", [g1, g2])
    rtu4 = LocalRTU("rtuLoads", [c1, c2, c3, c4])
    topology = [rtu1, rtu2, rtu3, rtu4]
    return topology


def initiateTopologyTransfFuseRelay():
    """
    Initialize TransfFuseRelay topology.
    :return: TransfFuseRelay topology
    """
    sw10 = Switch("rtu_global_sw10")
    sw11 = Switch("rtu_global_sw11")
    sw21 = Switch("rtu_global_sw21")
    sw22 = Switch("rtu_global_sw22")
    sw31 = Switch("rtu_global_sw31")
    sw32 = Switch("rtu_global_sw32")
    sw42 = Switch("rtu_global_sw42")
    sw43 = Switch("rtu_global_sw43")
    sw52 = Switch("rtu_global_sw52")
    sw53 = Switch("rtu_global_sw53")
    m10 = Meter("rtu_global_m10")
    m11 = Meter("rtu_global_m11")
    m21 = Meter("rtu_global_m21")
    m22 = Meter("rtu_global_m22")
    m31 = Meter("rtu_global_m31")
    m32 = Meter("rtu_global_m32")
    m42 = Meter("rtu_global_m42")
    m43 = Meter("rtu_global_m43")
    m52 = Meter("rtu_global_m52")
    m53 = Meter("rtu_global_m53")
    fu42 = Fuse("rtu_global_f42", 0.5, cuttingT=0)
    pr52 = ProtectiveRelay("rtu_global_pr52", 0.5, cuttingT=0)
    l1 = PowerLine("rtu_global_l1", 0.8, nominalV=10000, startSwitch=sw10, endSwitch=sw11, startMeter=m10, endMeter=m11)
    l2 = PowerLine("rtu_global_l2", 0.8, nominalV=10000, startSwitch=sw21, endSwitch=sw22, startMeter=m21, endMeter=m22)
    l3 = PowerLine("rtu_global_l3", 0.8, nominalV=10000, startSwitch=sw31, endSwitch=sw32, startMeter=m31, endMeter=m32)
    l4 = PowerLine("rtu_global_l4", 0.5, nominalV=230, startSwitch=sw42, endSwitch=sw43, startMeter=m42, endMeter=m43, startFuse=fu42)
    l5 = PowerLine("rtu_global_l5", 0.5, nominalV=230, startSwitch=sw52, endSwitch=sw53, startMeter=m52, endMeter=m53, startProtectiveRelay=pr52)
    bus1 = Bus("rtu_global_b1", [l1], [l2, l3])
    t1 = Transformer("rtu_global_t1", [l2], [l4], transformerRateFunction=lambda position: [40, 45, 50][int(round(position))])
    t2 = Transformer("rtu_global_t2", [l3], [l5], transformerRateFunction=lambda position: [40, 45, 50][int(round(position))])
    g1 = Generator("rtu_global_g1", [], [l1])
    c1 = Consumer("rtu_global_c1", [l4], [])
    c2 = Consumer("rtu_global_c2", [l5], [])
    rtu1 = LocalRTU("rtu1", [bus1, t1, t2])
    rtu2 = LocalRTU("rtu2", [g1])
    rtu3 = LocalRTU("rtu3", [c1, c2])
    topology = [rtu1, rtu2, rtu3]
    return topology


def initiateTopologyInterlock():
    """
    Initialize Interlock topology.
    :return: Interlock topology
    """
    sw11 = Switch("rtu_global_sw11")
    sw21 = Switch("rtu_global_sw21")
    sw31 = Switch("rtu_global_sw31")
    sw41 = Switch("rtu_global_sw41")
    il1 = StaticInterlock("rtu_global_interlock1", [sw21, sw31, sw41], guaranteedClosedSwitches=2)
    il2 = DynamicInterlock("rtu_global_interlock2", [sw21, sw31, sw41], guaranteedCurrent=2.0)
    m11 = Meter("rtu_global_m11")
    m21 = Meter("rtu_global_m21")
    m31 = Meter("rtu_global_m31")
    m41 = Meter("rtu_global_m41")
    l1 = PowerLine("rtu_global_l1", 5.0, nominalV=230, endSwitch=sw11, endMeter=m11)
    l2 = PowerLine("rtu_global_l2", 1.0, nominalV=230, startSwitch=sw21, startMeter=m21)
    l3 = PowerLine("rtu_global_l3", 1.0, nominalV=230, startSwitch=sw31, startMeter=m31)
    l4 = PowerLine("rtu_global_l4", 1.0, nominalV=230, startSwitch=sw41, startMeter=m41)
    l5 = PowerLine("rtu_global_l5", 5.0, nominalV=230)
    bus1 = Bus("rtu_global_b1", [l1], [l2, l3, l4])
    bus2 = Bus("rtu_global_b2", [l2, l3, l4], [l5])
    g1 = Generator("rtu_global_g1", [], [l1])
    c1 = Consumer("rtu_global_c1", [l5], [])
    rtu1 = LocalRTU("rtu1", [bus1])
    rtu2 = LocalRTU("rtu2", [g1, c1, bus2])
    topology = [rtu1, rtu2]
    return topology


def initiateTopologyMasterthesis():
    """
    Initialize topology of the master thesis evaluation.
    :return: Master thesis topology
    """
    # Switches
    # Generators
    sw10 = Switch("rtu_gencon_sw10")
    sw20 = Switch("rtu_gencon_sw20")
    sw11 = Switch("rtu_bus1_sw11")
    sw21 = Switch("rtu_bus1_sw21")
    # Bus 1
    sw31 = Switch("rtu_bus1_sw31")
    sw41 = Switch("rtu_bus1_sw41")
    sw51 = Switch("rtu_bus1_sw51")
    sw32 = Switch("rtu_bus2_sw32")
    sw42 = Switch("rtu_bus2_sw42")
    sw52 = Switch("rtu_bus2_sw52")
    # Bus 2
    sw62 = Switch("rtu_bus2_sw62")
    sw72 = Switch("rtu_bus2_sw72")
    sw63 = Switch("rtu_bus3_sw63")
    sw73 = Switch("rtu_bus3_sw73")
    # Bus 3
    sw83 = Switch("rtu_bus3_sw83")
    sw93 = Switch("rtu_bus3_sw93")
    sw84 = Switch("rtu_bus3t_sw84")
    sw94 = Switch("rtu_bus3t_sw94")
    # Transformers
    sw104 = Switch("rtu_bus3t_sw104")
    sw114 = Switch("rtu_bus3t_sw114")
    sw105 = Switch("rtu_gencon_sw105")
    sw115 = Switch("rtu_gencon_sw115")
    # Consumers

    # Interlocks
    il1 = DynamicInterlock("rtu_bus1_il1", [sw31, sw41, sw51], guaranteedCurrent=290)
    il2 = StaticInterlock("rtu_bus2_il2", [sw62, sw72], guaranteedClosedSwitches=1.0)

    # Meter
    # Generators
    m10 = Meter("rtu_gencon_m10")
    m20 = Meter("rtu_gencon_m20")
    m11 = Meter("rtu_bus1_m11")
    m21 = Meter("rtu_bus1_m21")
    # Bus 1
    m31 = Meter("rtu_bus1_m31")
    m41 = Meter("rtu_bus1_m41")
    m51 = Meter("rtu_bus1_m51")
    m32 = Meter("rtu_bus2_m32")
    m42 = Meter("rtu_bus2_m42")
    m52 = Meter("rtu_bus2_m52")
    # Bus 2
    m62 = Meter("rtu_bus2_m62")
    m72 = Meter("rtu_bus2_m72")
    m63 = Meter("rtu_bus3_m63")
    m73 = Meter("rtu_bus3_m73")
    # Bus 3
    m83 = Meter("rtu_bus3_m83")
    m93 = Meter("rtu_bus3_m93")
    m84 = Meter("rtu_bus3t_m84")
    m94 = Meter("rtu_bus3t_m94")
    # Transformers
    m104 = Meter("rtu_bus3t_m104")
    m114 = Meter("rtu_bus3t_m114")
    m105 = Meter("rtu_gencon_m105")
    m115 = Meter("rtu_gencon_m115")
    # Consumers

    # Fuses and Protective Relays
    fu104 = Fuse("rtu_bus3t_fu104", 500, cuttingT=5)
    pr114 = ProtectiveRelay("rtu_bus3t_pr114", 450, cuttingT=5)

    # Power Lines
    # Generators
    l1 = PowerLine("l1", 400, 10000, startSwitch=sw10, endSwitch=sw11, startMeter=m10, endMeter=m11)
    l2 = PowerLine("l2", 400, 10000, startSwitch=sw20, endSwitch=sw21, startMeter=m20, endMeter=m21)
    # Bus 1
    l3 = PowerLine("l3", 300, 10000, startSwitch=sw31, endSwitch=sw32, startMeter=m31, endMeter=m32)
    l4 = PowerLine("l4", 200, 10000, startSwitch=sw41, endSwitch=sw42, startMeter=m41, endMeter=m42)
    l5 = PowerLine("l5", 200, 10000, startSwitch=sw51, endSwitch=sw52, startMeter=m51, endMeter=m52)
    # Bus 2
    l6 = PowerLine("l6", 300, 10000, startSwitch=sw62, endSwitch=sw63, startMeter=m62, endMeter=m63)
    l7 = PowerLine("l7", 300, 10000, startSwitch=sw72, endSwitch=sw73, startMeter=m72, endMeter=m73)
    # Bus 3
    l8 = PowerLine("l8", 100, 10000, startSwitch=sw83, endSwitch=sw84, startMeter=m83, endMeter=m84)
    l9 = PowerLine("l9", 500, 10000, startSwitch=sw93, endSwitch=sw94, startMeter=m93, endMeter=m94)
    # Transformers
    l10 = PowerLine("l10", 500, 230, startSwitch=sw104, endSwitch=sw105, startMeter=m104, endMeter=m105, startFuse=fu104)
    l11 = PowerLine("l11", 450, 6000, startSwitch=sw114, endSwitch=sw115, startMeter=m114, endMeter=m115, startProtectiveRelay=pr114)
    # Consumers

    # Nodes
    g1 = Generator("rtu_gencon_g1", [], [l1])
    g2 = Generator("rtu_gencon_g2", [], [l2])
    bus1 = Bus("bus1", [l1, l2], [l3, l4, l5])
    bus2 = Bus("bus2", [l3, l4, l5], [l6, l7])
    bus3 = Bus("bus3", [l6, l7], [l8, l9])
    t1 = Transformer("rtu_bus3t_t1", [l8], [l10], transformerRateFunction=lambda position: [40, 45, 50, 55][int(round(position))])
    t2 = Transformer("rtu_bus3t_t2", [l9], [l11], transformerRateFunction=lambda position: [1.5, 1.6, 1.7, 1.8, 1.9][int(round(position))])
    c1 = Consumer("rtu_gencon_c1", [l10], [])
    c2 = Consumer("rtu_gencon_c2", [l11], [])

    rtu1 = LocalRTU("rtu1", [bus1])
    rtu2 = LocalRTU("rtu2", [bus2])
    rtu3 = LocalRTU("rtu3", [bus3, t1, t2])
    rtu4 = LocalRTU("rtu4", [g1, g2, c1, c2])
    topology = [rtu1, rtu2, rtu3, rtu4]
    return topology