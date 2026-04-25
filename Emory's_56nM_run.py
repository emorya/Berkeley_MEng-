# -*- coding: utf-8 -*-
from opentrons import protocol_api
from itertools import cycle

metadata = {
    "protocolName": "April 20th: Ratio Screen — 10 nM scaffold (1:2 and 1:5),
    "author": "TiLab",
    "description": (
        "Scaffold:staple ratio screen for 10 nM scaffold. "
        "p300 builds pools and condition tubes. p20 handles TC transfer and gel loading."
    ),
}

requirements = {"robotType": "OT-2", "apiLevel": "2.26"}
OFFSET = {"x":-0.5, "y": -2.5, "z": 16.5}
y_diff = -9

MINIONE_6_WELL_DEF = {
  "ordering":[["A1","B1","C1","D1","E1","F1"]],
  "brand":{"brand": "miniOne", "brandId":[]},
  "metadata":{
    "displayName": "MiniOne 6 Well Plate 10 µL",
    "displayCategory": "wellPlate",
    "displayVolumeUnits": "µL",
    "tags":[]
  },
  "dimensions":{
    "xDimension":127.76,
    "yDimension":85.47,
    "zDimension":84
  },
  "wells": {
    "A1": {"depth":8.13,"totalLiquidVolume":10,"shape":"rectangular",
           "xDimension":1.6,"yDimension":4.44,
           "x":93 + OFFSET["x"],
           "y":57.47 + (0 * y_diff) + OFFSET["y"],
           "z":54.87 + OFFSET["z"]},
    "B1": {"depth":8.13,"totalLiquidVolume":10,"shape":"rectangular",
           "xDimension":1.6,"yDimension":4.44,
           "x":93 + OFFSET["x"],
           "y":57.47 + (1 * y_diff) + OFFSET["y"],
           "z":54.87 + OFFSET["z"]},
    "C1": {"depth":8.13,"totalLiquidVolume":10,"shape":"rectangular",
           "xDimension":1.6,"yDimension":4.44,
           "x":93 + OFFSET["x"],
           "y":57.47 + (2 * y_diff) + OFFSET["y"],
           "z":54.87 + OFFSET["z"]},
    "D1": {"depth":8.13,"totalLiquidVolume":10,"shape":"rectangular",
           "xDimension":1.6,"yDimension":4.44,
           "x":93 + OFFSET["x"],
           "y":57.47 + (3 * y_diff) + OFFSET["y"],
           "z":54.87 + OFFSET["z"]},
    "E1": {"depth":8.13,"totalLiquidVolume":10,"shape":"rectangular",
           "xDimension":1.6,"yDimension":4.44,
           "x":93 + OFFSET["x"],
           "y":57.47 + (4 * y_diff) + OFFSET["y"],
           "z":54.87 + OFFSET["z"]},
    "F1": {"depth":8.13,"totalLiquidVolume":10,"shape":"rectangular",
           "xDimension":1.6,"yDimension":4.44,
           "x":93 + OFFSET["x"],
           "y":57.47 + (5 * y_diff) + OFFSET["y"],
           "z":54.87 + OFFSET["z"]},
  },
  "groups":[{
    "metadata":{"wellBottomShape":"flat"},
    "wells":["A1","B1","C1","D1","E1","F1"]
  }],
  "parameters":{
    "format":"irregular",
    "quirks":[],
    "isTiprack":False,
    "isMagneticModuleCompatible":False,
    "loadName":"minione_6_wellplate_10ul"
  },
  "namespace":"custom_beta",
  "version":1,
  "schemaVersion":2,
  "cornerOffsetFromSlot":{"x":0,"y":0,"z":0}
}

Z_FAST = 25
Z_SLOW = 8

# ============================================================
# REAGENT PREP — do these steps manually before the run
# ============================================================
#
# 1x TAE:
#    20 uL of 50x TAE + 980 uL MQ water = 1 mL at 1x TAE
#
# 10x TAE+ 125 mM MgCl2 stock  (tube A1):
#    200 uL of 50x TAE + 125 uL 1 M MgCl2 + 675 uL MQ Water
#
# Scaffold 42 nM working stock (tube A2):
    # 20 uL of 420 nM M13 stock + 180 uL 1x TAE = 200 uL at 44 nM
    # (1x TAE: 20 uL of 50x TAE + 980 uL MQ water)
#
# MQ water (tube A3):
#    Fill with at least 500 uL MQ water
#
#
# Master mix (tube A6): leave empty — robot fills
#    5.5x batch: 23.10 uL 10x TAE with 12.5mM MgCl2 + 55.00 uL scaffold = 78.10 uL
#    (14.20 uL pulled per condition = 4.20 uL buffer + 10.00 uL scaffold)
#
# Condition tubes B1-B4: leave empty — robot fills
#
# Loading dye (tube D2): fill as supplied (~50 uL)
# DNA ladder  (tube D3): ladder 1kb +  9.6 µL, 182.4 water  µL + loading dye  48 µL
#
# Deck layout:
#   1  = empty :) 
#   2  = MiniOne gel plate
#   4  = p20 tip rack
#   5  = p20 tip rack
#   6  = p300 tip rack
#   7/10 = Thermocycler
#   9  = Eppendorf 24-tube rack
#   11 = Falcon tube rack (freed by TC patch)
#
# Eppendorf rack (slot 9):
#   A1 = 10x TAE with 12.5mM MgCl2    A2 = scaffold 84 nM   A3 = MQ water
#   A4 = empty   A5 = empty    A6 = empty (master mix)
#   B1-B4 = empty condition tubes
#   D2 = loading dye , D3 = ladder , D5 = DNA STAPLES!! 

# (scaf_nM, ratio, staple_nM, pool, staple_vol_uL, water_vol_uL)
CONDITION_VOLS = [
    (5, "1:2", 50, "master",  7.50, 27.40),  # staple from master (56nM)
    (5, "1:5", 70, "master", 18.75, 16.15),  # staple from master (56nM)
    ]


CONDITION_TUBE_WELLS = ['B1','B2']
MASTER_MIX_VOL = 14.2   # uL per condition (4.20 buffer + 10.00 scaffold)
TOTAL_VOL = 42.0


def run(protocol: protocol_api.ProtocolContext):

    protocol.default_speed = 180

    # Tip racks
    tiprack_300 = protocol.load_labware("opentrons_96_tiprack_300ul", "6")
    tiprack_20a = protocol.load_labware("opentrons_96_tiprack_20ul",  "4")
    tiprack_20b = protocol.load_labware("opentrons_96_tiprack_20ul",  "5")

    # Pipettes
    p20  = protocol.load_instrument("p20_single_gen2",  "left",  tip_racks=[tiprack_20a, tiprack_20b])
    p300 = protocol.load_instrument("p300_single_gen2", "right", tip_racks=[tiprack_300])

    # Default flow rates
    p20.flow_rate.aspirate  = 5.56
    p20.flow_rate.dispense  = 7.56
    p300.flow_rate.aspirate = 60
    p300.flow_rate.dispense = 60
    
    p300.starting_tip = tiprack_300['A1']
    p20.starting_tip = tiprack_20a['C2']
    
    protocol.set_rail_lights(True)

    # Labware
    dna_mix_tube = protocol.load_labware(
        "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "9"
    )
    dna_mix_tube.set_offset(z=0, x=-.35, y=2)

    tc_mod = protocol.load_module("thermocyclerModuleV1")
    tc_plate = tc_mod.load_labware("nest_96_wellplate_100ul_pcr_full_skirt")

    try:
        import opentrons.motion_planning.deck_conflict as _deck_conflict
        def _patched_slots_covered(thermocycler):
            return {"7", "10"}
        _deck_conflict._ot2_slots_covered_by_thermocycler = _patched_slots_covered
    except (ImportError, AttributeError):
        pass

    TC_OFFSET_X = -23.28
    tc_plate.set_offset(x=TC_OFFSET_X, y=0, z=10)

    tube_rack_11 = protocol.load_labware(
        "opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical", "11",
        label="Slot 11 (Freed)"
    )

    minione_plate = protocol.load_labware_from_definition(
        MINIONE_6_WELL_DEF, "2"
    )

    # ------------------------------------------------------------------
    # Tube assignments
    # ------------------------------------------------------------------
    buffer10x_tube   = dna_mix_tube["A1"]
    scaffold_src     = dna_mix_tube["A2"]
    water_tube       = dna_mix_tube["A3"]
    master_mix_tube  = dna_mix_tube["A6"]
    pool40_tube      = dna_mix_tube["C2"]
    pool20_tube      = dna_mix_tube["C3"]
    loading_dye_tube = dna_mix_tube["D2"]
    ladder_tube      = dna_mix_tube["D3"]
    master_pool_tube = dna_mix_tube["D5"]
    scaffold_prep_tube = dna_mix_tube["A4"]  # robot fills: scaffold + dye for B1 lane

    condition_tubes = [dna_mix_tube[w] for w in CONDITION_TUBE_WELLS]
    tc_dest_wells   = [tc_plate[f"A{i}"] for i in range(1, len(CONDITION_VOLS) + 1 )]

#     # ------------------------------------------------------------------
#     # p300 transfer helper
#     # ------------------------------------------------------------------
# changed to .bottom(1)
    def p300_xfer(vol, src, dst, src_z=1): 
        p300.pick_up_tip()
        p300.move_to(src.top())
        p300.move_to(src.bottom(src_z), speed=20)
        p300.aspirate(vol, src.bottom(src_z))
        p300.move_to(src.top(), speed=60)
        p300.move_to(dst.top(), speed=80)
        p300.move_to(dst.bottom(src_z), speed=20)
        p300.dispense(vol, dst.bottom(src_z))
        p300.blow_out(dst.top())
        p300.drop_tip()

    def p20_xfer(vol, src, dst, src_z=1):
        p20.pick_up_tip()
        p20.move_to(src.top())
        p20.move_to(src.bottom(src_z), speed=20)
        p20.aspirate(vol, src.bottom(src_z))
        p20.touch_tip(src)
        p20.move_to(src.top(), speed=60)
        p20.move_to(dst.top(), speed=80)
        p20.move_to(dst.bottom(src_z), speed=20)
        p20.dispense(vol, dst.bottom(src_z))
        p20.blow_out(dst.top()) 
        p20.drop_tip()


#     # ==================================================================
#     # STEP 1 — p300 builds master mix in A6
#     # ==================================================================

        p300.pick_up_tip()
        p300.move_to(buffer10x_tube.top())
        p300.move_to(buffer10x_tube.bottom(1))
        protocol.pause()
        p300.move_to(buffer10x_tube.bottom(1))
        protocol.pause()
        protocol.delay(minutes=0.1)
        p300.move_to(buffer10x_tube.bottom(1))
        p300.move_to(master_mix_tube.bottom(1))
        protocol.pause()
        protocol.delay(minutes=0.1)
        p300.move_to(master_mix_tube.bottom(1))
        protocol.pause()
        protocol.delay(minutes=0.1)
        p300.move_to(master_mix_tube.bottom(1))
    



    #5.5x batch: 23.10 uL buffer + 55.00 uL scaffold = 78.10 uL total
    protocol.comment("=== Step 1: Build master mix in A6 ===")

    p300_xfer(23.10, buffer10x_tube, master_mix_tube)
    p300_xfer(55.00, scaffold_src, master_mix_tube)

    p300.pick_up_tip()
    p300.mix(3, 50, master_mix_tube.bottom(1))
    p300.blow_out(master_mix_tube.top())
    p300.drop_tip()
    
#     # ==================================================================
#     # STEP 2 — p300 builds 5 condition tubes
#     # ==================================================================
    # protocol.comment("=== Step 4: Build 5 condition tubes ===")
    p20.flow_rate.aspirate = 3.0
    p20.flow_rate.dispense = 5.0
    
    pool_map = {
        "master": master_pool_tube,
    }

    for i, (scaf_nM, ratio, stap_nM, pool, st_vol, w_vol) in enumerate(CONDITION_VOLS):
        dest = condition_tubes[i]
        pool_src = pool_map[pool]

        protocol.comment(f"  Condition {i+1}: scaf={scaf_nM}nM {ratio}  mix={MASTER_MIX_VOL} stap={st_vol} water={w_vol} uL  pool={pool}")

        p300_xfer(MASTER_MIX_VOL, master_mix_tube, dest)
        p20_xfer(st_vol, pool_src, dest, src_z=1 if pool == "master" else 2)
        if w_vol > 0:
            p300_xfer(w_vol, water_tube, dest)

        p300.pick_up_tip()
        p300.mix(2, 30, dest.bottom(1))
        p300.blow_out(dest.top())
        p300.drop_tip()

    # # ==================================================================
    # # STEP 3 — transfers to TC plate
    # # ==================================================================
    # protocol.comment("=== Step 4: Transfer to TC ===")

    p20.flow_rate.aspirate = 3.0 

    tc_mod.open_lid()
    for i, src in enumerate(condition_tubes):
    # Transfer 15 uL sample to TC plate
        p20.pick_up_tip()
        p20.aspirate(15, src.bottom(1))
        p20.dispense(15, tc_dest_wells[i].bottom(2))
        p20.blow_out(tc_dest_wells[i].top())

        
        p20.aspirate(15, src.bottom(1))
        p20.dispense(15, tc_dest_wells[i].bottom(2))
        p20.blow_out(tc_dest_wells[i].top())



        p20.drop_tip()

        

    # protocol.comment("=== Thermocycler profile (65C -> 20C) ===")

    tc_mod.close_lid()
    tc_mod.set_lid_temperature(105)
 
    # Step 1: 95°C hold for 2 minutes
    # Steps 2: 95°C → 65°C, drop 0.1°C every 6 seconds (300 steps)
    # Step 3: 65°C → 20°C, drop 0.1°C every 12 seconds (450 steps)
    profile = (
        [{"temperature": 95.0, "hold_time_seconds": 120}]
        + [{"temperature": round(95 - 0.1 * i, 1), "hold_time_seconds": 6}
           for i in range(1, 301)]
        + [{"temperature": round(65 - 0.1 * i, 1), "hold_time_seconds": 12}
           for i in range(1, 451)]
    )
    tc_mod.execute_profile(
        steps=profile,
        repetitions=1,
        block_max_volume=30
    )


    # ==================================================================
    # Step 4- Thermocycler opens and ready to add dye for gel loading
    # ==================================================================

    tc_mod.deactivate_lid()
    tc_mod.deactivate_block()

    protocol.pause("SYNC:OPEN_GEL_LID")
    protocol.pause("Thermocycler Done. Resume when ready. ADD GEL and BUFFER AND OPEN p20s and eppendorf CAPS")
    protocol.pause("SYNC:CLOSE_GEL_LID")
    
    protocol.default_speed = 50

    tc_mod.open_lid()
    protocol.pause("AFM samples?")

    # Add loading dye to TC wells
    loading_dye_uL = 6.75
    
    protocol.comment("=== Adding loading dye to TC wells ===")
    for well in tc_dest_wells:
        p20.pick_up_tip()
        p20.aspirate(loading_dye_uL, loading_dye_tube.bottom(1))
        p20.dispense(loading_dye_uL, well.bottom(2))
        p20.mix(2, 10, well.bottom(2))
        p20.blow_out(well.top())
        p20.drop_tip()

    # # ==================================================================
    # # STEP 5 — p20 gel loading
    # # ==================================================================
    # protocol.comment("=== Step 5: Gel electrophoresis ===")
    protocol.pause("SYNC:OPEN_GEL_LID")

    gel_lanes = ['C1','D1']
    sample_uL = 16 
    ladder_uL = 5.0
    scaffold_lane_uL = 5.0  # 3.5 uL scaffold + 1.5 uL dye

    # Lower dispense speed for gel loading
    p20.flow_rate.dispense = 2

    sources = tc_dest_wells
    dests  = [minione_plate[w] for w in gel_lanes]

    for src, dst in zip (sources, dests):

        p20.pick_up_tip()
        p20.aspirate(sample_uL, src.bottom(0))
        p20.move_to(dst.top(), speed=Z_FAST)
        p20.move_to(dst.top(-3), speed=Z_SLOW)
        p20.dispense(sample_uL, dst.top(-3))

        p20.drop_tip()
        
    # protocol.pause("Make sure ladder is in the rack") 
    ladder_well = minione_plate["A1"]

    p20.pick_up_tip()
    p20.aspirate(ladder_uL, ladder_tube.bottom(0))
    p20.move_to(ladder_well.top(), speed=Z_FAST)
    p20.move_to(ladder_well.top(-3), speed=Z_SLOW)
    p20.dispense(ladder_uL, ladder_well.top(-3))
    p20.drop_tip()

    protocol.pause("Add Scaffold back into rack and make sure you have A4 empty tube next to it")

    # Prep scaffold lane: transfer scaffold (A2) + dye into A4, then load into gel A1
    protocol.comment("=== Prep scaffold lane: scaffold + dye → A4 ===")
    p20.pick_up_tip()
    p20.aspirate(3.5, scaffold_src.bottom(1))
    p20.dispense(3.5, scaffold_prep_tube.bottom(1))
    p20.blow_out(scaffold_prep_tube.top())
    p20.drop_tip()

    p20.pick_up_tip()
    p20.aspirate(1.5, loading_dye_tube.bottom(1))
    p20.dispense(1.5, scaffold_prep_tube.bottom(1))
    p20.mix(2, 4, scaffold_prep_tube.bottom(1))
    p20.blow_out(scaffold_prep_tube.top())
    p20.drop_tip()

    scaffold_lane_well = minione_plate["B1"]

    p20.pick_up_tip()
    p20.aspirate(scaffold_lane_uL, scaffold_prep_tube.bottom(0))
    p20.move_to(scaffold_lane_well.top(), speed=Z_FAST)
    p20.move_to(scaffold_lane_well.top(-3), speed=Z_SLOW)
    p20.dispense(scaffold_lane_uL, scaffold_lane_well.top(-3))
    p20.drop_tip()



    protocol.pause("Add Hand-Made DNA")
    protocol.pause("SYNC:CLOSE_GEL_LID")
    protocol.pause("SYNC:GEL_POWER_ON")
    protocol.pause("SYNC:LIGHT_ON")
    protocol.set_rail_lights(False)
    protocol.pause("SYNC:START_TIMELAPSE")
    protocol.delay(minutes=25)
    protocol.pause("SYNC:GEL_POWER_OFF")
    protocol.pause("SYNC:LIGHT_OFF")
    protocol.pause("SYNC:STOP_TIMELAPSE")
    protocol.pause("SYNC:OPEN_GEL_LID")
    protocol.comment("=== Protocol complete ===")
