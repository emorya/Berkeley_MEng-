# -*- coding: utf-8 -*-
from opentrons import protocol_api

metadata = {
    "protocolName": "Make Master Conical — Pool plate to 56nM per staple",
    "author": "TiLab",
    "description": (
        "Transfers 10 uL from pre-diluted pool plate wells into a 15 mL conical. "
    ),
}
requirements = {"robotType": "OT-2", "apiLevel": "2.16"}


def run(protocol: protocol_api.ProtocolContext):
    protocol.default_speed = 50

    tiprack_20a = protocol.load_labware("opentrons_96_tiprack_20ul", "4")
    p20 = protocol.load_instrument("p20_single_gen2", "left", tip_racks=[tiprack_20a])

    # THIS MUST BE CHECKED EACH RUN
    p20.starting_tip = tiprack_20a['B6']

    p20.flow_rate.aspirate = 3.78
    p20.flow_rate.dispense = 7.56

    protocol.set_rail_lights(True)

    pool_plate = protocol.load_labware("nest_96_wellplate_100ul_pcr_full_skirt", "3")

    falcon_rack = protocol.load_labware(
        "opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical", "6",
        label="Slot 11 (Freed)"
    )
    master_conical = falcon_rack["A4"]  # empty 15mL tube — robot fills

    # 46 pool wells, skipping B5 and C9
    pool_wells = [pool_plate[w] for w in [
        "A1","A2","A3","A4","A5","A6","A7","A8","A9","A10","A11","A12",
        "B1","B2","B3","B4","B6","B7","B8","B9","B10","B11","B12",
        "C1","C2","C3","C4","C5","C6","C7","C8","C10","C11","C12",
        "D1","D2","D3","D4","D5","D6","D7","D8","D9","D10","D11","D12",
    ]]

    protocol.comment("=== Transferring 10 uL from each of 45 pool wells to master conical ===")

    for well in pool_wells:
        p20.pick_up_tip()
        p20.move_to(well.top(z=10))
        p20.move_to(well.bottom(0.5), speed=20)
        p20.aspirate(10, well.bottom(0.5))
        p20.move_to(well.top(z=10), speed=20)
        p20.move_to(master_conical.bottom(2), speed=80)
        p20.dispense(10, master_conical.bottom(2))
        p20.blow_out(master_conical.top())
        p20.blow_out(master_conical.top())
        p20.drop_tip()

    protocol.set_rail_lights(False)
    protocol.comment("=== Protocol complete ===")
