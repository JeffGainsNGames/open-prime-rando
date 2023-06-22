from retro_data_structures.enums import echoes
from retro_data_structures.properties.echoes.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.echoes.archetypes.WeaponVulnerability import WeaponVulnerability

reflect = WeaponVulnerability(damage_multiplier=0, effect=echoes.Effect.Reflect)
vulnerable = WeaponVulnerability(damage_multiplier=100, effect=echoes.Effect.Normal)
immune = WeaponVulnerability(damage_multiplier=0, effect=echoes.Effect.Normal, ignore_radius=True)


resist_all_vuln = DamageVulnerability(
    power=reflect, dark=reflect, light=reflect, annihilator=reflect,
    power_charge=reflect, entangler=reflect, light_blast=reflect, sonic_boom=reflect,
    super_missle=reflect, black_hole=reflect, sunburst=reflect, imploder=reflect,

    boost_ball=immune, cannon_ball=immune, screw_attack=immune, bomb=immune, power_bomb=immune,
    missile=immune, phazon=reflect, ai=immune, poison_water=immune, dark_water=immune, lava=immune,
    area_damage_hot=immune, area_damage_cold=immune, area_damage_dark=immune, area_damage_light=immune,
    weapon_vulnerability=immune, normal_safe_zone=immune,
)
