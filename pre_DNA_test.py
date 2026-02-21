# -*- coding: utf-8 -*-
from opentrons import protocol_api
from itertools import cycle

metadata = {
    "protocolName": "MOthER FUCKING Liquid retention test: FULL RUN with Yifeng picklist for 384 plate",
    "author": "TiLab",
    "description": "1) Adding reagents to destination tube: TAE Buffer, Water, M18 Scaffold 2) Adding dna from Picklist to destination tube, Putting into Thermocycler, 3)Thermocycler to Gel Electrophoresis ",
}

requirements = {"robotType": "OT-2", "apiLevel": "2.26"}

# ------------------------------------------------------------
# Global calibration offset (mm)
# Change this if plate positioning shifts.
# ------------------------------------------------------------
OFFSET = {"x": 1.5, "y": -5.7, "z": -2.5} # I want these to be zero by final run 
y_diff = -9.0


MINIONE_6_WELL_DEF = {
  "ordering":[["A1","B1","C1","D1","E1","F1"]],
  "brand":{"brand":"miniOne","brandId":[]},
  "metadata":{
    "displayName":"MiniOne 6 Well Plate 10 µL",
    "displayCategory":"wellPlate",
    "displayVolumeUnits":"µL",
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
           "y":57.47 + 0 * y_diff + OFFSET["y"],
           "z":54.87 + OFFSET["z"]},

    "B1": {"depth":8.13,"totalLiquidVolume":10,"shape":"rectangular",
           "xDimension":1.6,"yDimension":4.44,
           "x":93 + OFFSET["x"],
           "y":57.47 + 1 * y_diff + OFFSET["y"],
           "z":54.87 + OFFSET["z"]},

    "C1": {"depth":8.13,"totalLiquidVolume":10,"shape":"rectangular",
           "xDimension":1.6,"yDimension":4.44,
           "x":93 + OFFSET["x"],
           "y":57.47 + 2 * y_diff + OFFSET["y"],
           "z":54.87 + OFFSET["z"]},

    "D1": {"depth":8.13,"totalLiquidVolume":10,"shape":"rectangular",
           "xDimension":1.6,"yDimension":4.44,
           "x":93 + OFFSET["x"],
           "y":57.47 + 3 * y_diff + OFFSET["y"],
           "z":54.87 + OFFSET["z"]},

    "E1": {"depth":8.13,"totalLiquidVolume":10,"shape":"rectangular",
           "xDimension":1.6,"yDimension":4.44,
           "x":93 + OFFSET["x"],
           "y":57.47 + 4 * y_diff + OFFSET["y"],
           "z":54.87 + OFFSET["z"]},

    "F1": {"depth":8.13,"totalLiquidVolume":10,"shape":"rectangular",
           "xDimension":1.6,"yDimension":4.44,
           "x":93 + OFFSET["x"],
           "y":57.47 + 5 * y_diff + OFFSET["y"],
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




Z_FAST = 25     # mm/s — approach
Z_SLOW = 8      # mm/s — final descent

# ---------------------------------------------------------------------
# MAIN PROTOCOL
# ---------------------------------------------------------------------

def run(protocol: protocol_api.ProtocolContext): 

    #this is the speed of the whole run unless overwritten for -certain- steps 
    protocol.default_speed = 180 

    #Deck locations for each p20 pipette tip plate 
    tiprack_20a = protocol.load_labware("opentrons_96_tiprack_20ul", "1")
    tiprack_20b = protocol.load_labware("opentrons_96_tiprack_20ul", "4")
    tiprack_20c = protocol.load_labware("opentrons_96_tiprack_20ul", "5")
    
    # Pipette easy variable 
    p20 = protocol.load_instrument("p20_single_gen2",  "left",  tip_racks=[tiprack_20a, tiprack_20b, tiprack_20c])  

    # This is how fast our pipette take in and push out fluid 
    p20.flow_rate.aspirate = 7.56
    p20.flow_rate.dispense = 7.56

    # Turn the lights on!
    protocol.set_rail_lights(True)
    
    # Load labware
    source_384 = protocol.load_labware(
        "beckmancoulter_384_wellplate_60ul", "6"
    )
    
    # dna_mix_tube= protocol.load_labware(
    #     "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "9"
    # )
    # dna_mix_tube.set_offset(z=0, x=-1, y=1)

    # Tube rack for reagents
    dna_mix_tube = protocol.load_labware(
        "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "9"
    )
    dna_mix_tube.set_offset(z=0, x=-.35, y=2)


    # Thermocycler
    tc_mod = protocol.load_module("thermocyclerModuleV1")
    tc_plate = tc_mod.load_labware("nest_96_wellplate_100ul_pcr_full_skirt")

    # This is going to make it so we can use slots 8 and 11 
    try:
        import opentrons.motion_planning.deck_conflict as _deck_conflict

        def _patched_slots_covered(thermocycler):
            # Treat TC as only covering slots 7 and 10 so slots 8 and 11 can be used
            return {"7", "10"}

        _deck_conflict._ot2_slots_covered_by_thermocycler = _patched_slots_covered

    except (ImportError, AttributeError):
        pass

    TC_OFFSET_X = -23.28

    
    tc_plate.set_offset(x=TC_OFFSET_X, y=0, z=10)
    
    plate_8 = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', 8, label="Slot 8 (Freed)")
    tube_rack_11 = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', 11, label="Slot 11 (Freed)")


    # MiniOne Gel Electrophoresis  
    minione_plate = protocol.load_labware_from_definition(
        MINIONE_6_WELL_DEF, "2"
    )

    #----------STEP 1 ----------------
    # Least expensive substances first
  
    # NEED TO CHANGE TIPS EVERY DNA RUN  
    protocol.comment("=== Step 1: Build dna  mix on 96-well plate===")

    wells = [f"A{i}" for i in range(1, 7)]
    
    # Reagents are now in the conical tube rack (dna _mix_tube)
    buffer10x_tube = dna_mix_tube["A1"]  # 10x Mg-TAE
    
    scaffold_tube = dna_mix_tube["A2"]

    water_tube = dna_mix_tube["A3"]
    
    # (Optional) mgcl2_tube placeholder if you later want it:
    mgcl2_tube = dna_mix_tube["A4"]

    # Destination tube in the Falcon tube rack
    dest_tube = dna_mix_tube["A6"]

    loading_dye_tube = dna_mix_tube["B1"]
    
    ladder_tube = dna_mix_tube["B2"]

      # Volumes (uL) for 21.0 uL dna  mix
   # ---------- DNA mix volumes (NO MgCl2) ----------
    vol_scaffold = 16.66
    vol_buffer10x = 2.10
    vol_water = 2.24

    #THIS SHIT BETTER WORK 
    p20.starting_tip = tiprack_20a['A7']

    def add_to_mix(vol_uL, src, label):
        protocol.comment(f"Add {label}: {vol_uL} uL")
        p20.pick_up_tip()
        p20.move_to(src.top())
        p20.move_to(src.bottom(2), speed=20)
        p20.aspirate(vol_uL, src.bottom(1)) 
        p20.move_to(src.top(), speed=60)

        p20.move_to(dest_tube.top(), speed=80)
        p20.move_to(dest_tube.bottom(2), speed=20)
        p20.dispense(vol_uL, dest_tube.bottom(2))
        # p20.blow_out(dest_tube.top(-1.5))
        # p20.blow_out(dest_tube.top(-1))
        p20.blow_out(dest_tube.top())
        p20.drop_tip()

    protocol.comment("=== Step 1: Build DNA mix in A6 ===")
    add_to_mix(vol_buffer10x, buffer10x_tube, "10x TAE")
    add_to_mix(vol_scaffold, scaffold_tube, "scaffold")
    add_to_mix(vol_water, water_tube, "water")

#     # OPTIONAL Mix
#     p20.pick_up_tip()
#     p20.mix(2,15, dest_tube.bottom(5))
#     p20.blow_out(dest_tube.top(-2))
#     p20.blow_out(dest_tube.top())
#     p20.drop_tip()

     # These are the coordinates of the DNA STAPLE picklist 
    yifeng_wells = [
     source_384[w] for w in [
         # "A2","A3","A5","A6","A7","A8","A9","A10","A11","A13","A14","A15","A16","A17","A18","A19","A20","A21","A22","A23","A24",
         # "B4","B5","B6","B7","B8","B9","B10","B11","B13","B14","B15","B16","B17","B18","B19","B20","B21","B22","B23","B24",
         # "C4","C5","C7","C8","C9","C10","C11","C13","C14","C15","C16","C17","C18","C19","C20","C21","C22","C23","C24",
         # "D2","D3","D4","D5","D7","D8","D9","D10","D11","D13","D14","D15","D16","D17","D18","D19","D20","D21","D22","D23","D24",
         # "E10","E11","E12","E13","E14","E15","E16",
         # "F4","F5","F10","F11","F16","F17","F22","F23",
         # "G3","G4","G5","G9","G10","G11","G15","G16","G17","G21","G22","G23",
         # "H11","H12","H13","H14","H15","H16","H17","H18","H19","H20","H21","H22","H23",
         # "I2","I3","I4","I5","I6","I8","I9","I10","I11",
         # "J2","J4","J5","J6","J7","J9","J10","J11",
         # "K3","K4","K6","K8","K9","K10","K11",
         # "L3","L6","L8","L10","L11",
         "M2","M3","M5","M6","M7","M8","M10","M11",
         "N2","N3","N4","N6","N7","N8","N9","N10","G9","N11",
         "O3","O5","O6","O8","O9","O10","O11",
         "P3","P5","P8","P9","P10"
     ]
 ]

     # slower for 1 uL
    p20.flow_rate.aspirate = 3
    p20.flow_rate.dispense = 3

    for well in yifeng_wells:
         p20.pick_up_tip()
         p20.move_to(well.top(z=10))
         p20.move_to(well.bottom(0.5), speed=20)
         p20.aspirate(1, well.bottom(0.5))
         p20.move_to(well.top(z=10), speed=20) #take out z= 10 if that's stupid 

         p20.move_to(dest_tube.bottom(2), speed=80)
         p20.dispense(1, dest_tube.bottom(2))
         # p20.blow_out(dest_tube.top(-1.5))
         # p20.blow_out(dest_tube.top(-1)) 
         p20.blow_out(dest_tube.top()) 
         p20.drop_tip()

   
    p20.flow_rate.aspirate = 7.56
    p20.flow_rate.dispense = 7.56


    
# #     # --------------------------------------------------
# #     # PART 1 — DNA Mix → Thermocycler + temp profile
# #     # ----------------------------- ---------------------
#     protocol.comment("=== Step 2 : DNAMix Plate → Thermocycler transfer ===")
        
    tc_mod.open_lid()
        
    xfer_to_tcplate_uL = 10
    
    tc_dest_wells = [tc_plate[f"A{i}"] for i in range(1, 6)]
    
     # Choose staple source wells from the 384-well plate (example: A1–A6)
    src = dna_mix_tube["A6"]
    
    for dest in tc_dest_wells:
         p20.pick_up_tip()
         p20.aspirate(xfer_to_tcplate_uL, src.bottom(1))
         p20.dispense(xfer_to_tcplate_uL, dest.bottom(2))
         p20.blow_out(dest.bottom(2))
         p20.drop_tip()

     #If there is water left in pipette try this 
     # for dest in [tc_plate["A1"], tc_plate["A2"], tc_plate["A3"]]:
     #     p20.pick_up_tip()
     #     p20.aspirate(10, dest_tube.bottom(2))
     #     p20.air_gap(1.0) 
     #     p20.dispense(10, dest.bottom(5))
     #     p20.blow_out(dest.top(-1.5))
     #     p20.blow_out(dest.top(-1))
     #     p20.blow_out(dest.top())
     #     p20.drop_tip()

    

         # --- Thermocycler profile ---
    protocol.comment("=== Thermocycler profile (65°C → 20°C) ===")
    
    tc_mod.set_lid_temperature(100)
    tc_mod.close_lid()
    
    profile = [
         {"temperature": round(65 - 0.1 * i, 1), "hold_time_seconds": 12}
         for i in range(0, 451)   # 450 steps: 65.0 → 20.0
     ]
    
    tc_mod.execute_profile(
         steps=profile,
         repetitions=1,
         block_max_volume=60
     )
    
    tc_mod.open_lid()
    tc_mod.deactivate_lid()
    tc_mod.deactivate_block()


    tc_mod.execute_profile(
         steps=profile,
         repetitions=1,
         block_max_volume=60
     )

    tc_mod.open_lid()
    tc_mod.deactivate_lid()
    tc_mod.deactivate_block()



    # --------------------------------------------------
    # PART 2 —Thermo → MiniOne cyclic transfer
    # --------------------------------------------------

    protocol.comment("=== Step 4: Thermo → MiniOne transfer ===")

    sources = [tc_plate[f"A{i}"] for i in range(1, 6)]
    dests = [minione_plate[w] for w in ["B1","C1","D1","E1","F1"]]

    for src, dst in zip(cycle(sources), dests):

        p20.pick_up_tip()
        p20.flow_rate.dispense = 3

    # Aspirate
        p20.aspirate(5, src.bottom(1))

    #Try once and remove if you don't like it 

        #p20.air_gap(1.0)

    # Move above destination (normal XY, controlled Z)
        p20.move_to(dst.top(), speed=Z_FAST)

    # Slow descent into MiniOne well
        p20.move_to(dst.bottom(1.5), speed=Z_SLOW)

    # Dispense + blowout
        p20.dispense(5, dst.bottom(0.5))
        p20.blow_out(dst.top(-2)) #this may need to be changed !! 

        p20.drop_tip()

    protocol.comment("=== Step: Add loading dye + ladder ===")

    dye_uL = 1.5
    ladder_uL = 5.0
    
    dna_gel_wells = [minione_plate[w] for w in ["B1","C1","D1","E1","F1"]]
    
    for gel_well in dna_gel_wells:
        p20.pick_up_tip()
        p20.aspirate(dye_uL, loading_dye_tube.bottom(1))
        p20.dispense(dye_uL, gel_well.bottom(1))
        p20.blow_out(gel_well.top(-1))
        p20.drop_tip()
        
    ladder_well = minione_plate["A1"]

    p20.pick_up_tip()
    p20.aspirate(6, ladder_tube.bottom(1))
    p20.dispense(6, ladder_well.bottom(1))
    p20.blow_out(ladder_well.top(-1))
    p20.drop_tip()


    
    protocol.set_rail_lights(False)
    protocol.comment("=== Protocol complete ===")
