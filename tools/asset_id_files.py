import argparse
import os.path
from pathlib import Path

import retro_data_structures.exceptions
from retro_data_structures.asset_manager import IsoFileProvider
from retro_data_structures.formats import Mrea, Strg
from retro_data_structures.game_check import Game
from retro_data_structures.properties.shared_objects import Dock

from open_prime_rando.patcher_editor import PatcherEditor
from open_prime_rando.unique_area_name import CUSTOM_AREA_NAMES

_CUSTOM_WORLD_NAMES = {
    Game.ECHOES: {
        0x69802220: "FrontEnd",
        0xA50A80CC: "M01_SidehopperStation",
        0xAE171602: "M02_Spires",
        0xE3B0C703: "M03_CrossfireChaos",
        0x233E42BE: "M04_Pipeline",
        0x406ADD7F: "M05_SpiderComplex",
        0x7E19ED26: "M06_ShootingGallery",
    }
}
_CUSTOM_AREA_NAMES = {
    Game.ECHOES: CUSTOM_AREA_NAMES,
}


# Complexity
# ruff: noqa: C901

def filter_name(s: str) -> str:
    result = s.replace("!", "").replace(" ", "_").replace("'", "").replace(
        '"', "").replace("(", "").replace(")", "").upper()
    while result and not result[0].isalpha():
        result = result[1:]
    return result


def dock_name_templates(dock_names: dict[str, dict[str, int]]) -> str:
    template = "\nDOCK_NAMES = {\n"
    for name in sorted(dock_names.keys()):
        template += f"    \"{name}\": {{\n"
        for dock_name, dock_number in sorted(dock_names[name].items(), key=lambda it: it[1]):
            template += f"        \"{dock_name}\": {dock_number},\n"
        template += "    },\n"
    template += "}\n"

    return template


def generate_template(items: dict[str, int], suffix: str) -> str:
    template = f"# Generated by {os.path.basename(__file__)}\n\n"
    template += "\n".join(
        f"{filter_name(key)}{suffix} = 0x{items[key]:08X}"
        for key in sorted(items)
    )
    template += "\n"

    template += f"\nNAME_TO_ID{suffix}" + " = {\n"
    for name in sorted(items):
        template += f"    \"{name}\": 0x{items[name]:08X},\n"
    template += "}\n"

    return template


def create_asset_id_files(editor: PatcherEditor, output_path: Path):
    output_path.mkdir(parents=True, exist_ok=True)

    custom_world_names = _CUSTOM_WORLD_NAMES.get(editor.target_game, {})
    world_names = {}
    mapw_names = {}

    for value in editor.all_asset_ids():
        if editor.get_asset_type(value).lower() != "mlvl":
            continue

        mlvl = editor.get_mlvl(value)

        try:
            strg = editor.get_file(mlvl.raw.world_name_id, type_hint=Strg)
            world_name = strg.raw.string_tables[0].strings[0].string
        except retro_data_structures.exceptions.UnknownAssetId:
            if value not in custom_world_names:
                print(f"Skipping MLVL {value}: no name found")
                continue
            world_name = custom_world_names[value]

        world_names[world_name] = value
        mapw_names[world_name] = mlvl.raw.world_map_id

        area_names = {}
        mapa_names = {}
        dock_names = {}

        for area, mapa in zip(mlvl.raw.areas, mlvl.mapw.mapa_ids):
            try:
                strg = editor.get_file(area.area_name_id, type_hint=Strg)
                area_name = strg.raw.string_tables[0].strings[0].string
            except retro_data_structures.exceptions.UnknownAssetId:
                area_name = area.internal_area_name
            area_name = _CUSTOM_AREA_NAMES[editor.target_game].get(area.area_mrea_id, area_name)

            if area_name in area_names:
                area_name += "_2"
            assert area_name not in area_names, area_name
            area_names[area_name] = area.area_mrea_id
            mapa_names[area_name] = mapa
            mrea = editor.get_file(area_names[area_name], type_hint=Mrea)

            docks = {}
            for layer in mrea.script_layers:
                for obj in layer.instances:
                    if obj.type_name == "DOCK":
                        dock: Dock = obj.get_properties_as(Dock)
                        assert dock.get_name() not in docks
                        docks[dock.get_name()] = dock.dock_number

                # Docks are in the default layer, ignore the rest
                break

            assert max(docks.values(), default=-1) == len(docks) - 1
            dock_names[area_name] = docks

        world_file_body = generate_template(area_names, "_MREA")
        world_file_body += generate_template(mapa_names, "_MAPA")
        world_file_body += dock_name_templates(dock_names)
        output_path.joinpath(f"{filter_name(world_name).lower()}.py").write_text(world_file_body)

    global_file_body = generate_template(world_names, "_MLVL")
    global_file_body += generate_template(mapw_names, "_MAPW")

    global_file_body += "\n_DEDICATED_FILES = {\n"
    for name in sorted(world_names.keys()):
        global_file_body += f"    \"{name}\": \".{filter_name(name).lower()}\",\n"
    global_file_body += """}


def load_dedicated_file(world_name: str):
    import importlib
    return importlib.import_module(
        _DEDICATED_FILES[world_name],
        ".".join(__name__.split(".")[:-1]),
    )
"""

    output_path.joinpath("world.py").write_text(global_file_body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", required=True, choices=["echoes"])
    parser.add_argument("--iso", required=True, type=Path,
                        help="Path to where the ISO.")
    args = parser.parse_args()

    create_asset_id_files(
        PatcherEditor(IsoFileProvider(args.iso), Game.ECHOES),
        Path(__file__).parents[1].joinpath("src", "open_prime_rando", args.game, "asset_ids"),
    )


if __name__ == '__main__':
    main()
