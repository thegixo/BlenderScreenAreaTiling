import bpy

from bpy.types import (
    Operator,
)

from bpy.props import (
    StringProperty,
)

# TODO if subarea gets deleted manually update the area_dictionary
# TODO find a way to store sub areas when the file closes so they would be recognized when file gets reopened

addon_keymaps = []
area_dictionary = {}


def get_areas():
    return area_dictionary


def _add_hotkey():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if not kc:
        print("Keymap Error")
        return

    km = kc.keymaps.new(name="Object Mode", space_type="EMPTY")
    # Adding "Alt" + "Space" as pie menu hotkey
    kmi = km.keymap_items.new(
        SAT_OT_PIE_tiling_ui_main_call.bl_idname, "SPACE", "PRESS", alt=True)
    addon_keymaps.append((km, kmi))


def _remove_hotkey():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()


class SAT_OT_split_area(Operator):
    bl_idname = "sat.split_area"
    bl_label = "Split Selected Area"
    bl_description = "Split selected screen area"

    direction: StringProperty(
        name="Direction",
        default="",
    )

    def execute(self, context):
        areas = bpy.context.screen.areas
        parent_area_pointer = str(bpy.context.area.as_pointer())
        pref = bpy.context.preferences.addons["ScreenAreaTiling"].preferences

        existing_areas = []
        existing_areas.clear()

        # Saving a list of existing areas
        for area in areas:
            existing_areas.append(area)

        if self.direction == "LEFT":
            factor = (pref.split_ratio_left)/100
            split_direction = "VERTICAL"
            area_type = pref.area_types_left

        elif self.direction == "RIGHT":
            factor = (100 - pref.split_ratio_right)/100
            split_direction = "VERTICAL"
            area_type = pref.area_types_right

        elif self.direction == "TOP":
            factor = (100 - pref.split_ratio_top)/100
            split_direction = "HORIZONTAL"
            area_type = pref.area_types_top

        elif self.direction == "BOTTOM":
            factor = (pref.split_ratio_bottom)/100
            split_direction = "HORIZONTAL"
            area_type = pref.area_types_bottom

        bpy.ops.screen.area_split(direction=split_direction, factor=factor)

        for new_area in areas:
            if new_area not in existing_areas:
                new_area.ui_type = area_type
                area_dictionary.update({parent_area_pointer+self.direction: new_area.as_pointer()})

        print(area_dictionary)

        return {"FINISHED"}


class SAT_OT_close_area(Operator):
    bl_idname = "sat.close_area"
    bl_label = "Close Selected Area"
    bl_description = "Close selected area"

    direction: StringProperty(
        name="Direction",
        default="",
    )

    def execute(self, context):
        parent_area_pointer = bpy.context.area.as_pointer()
        parent_area_key = str(parent_area_pointer)+self.direction
        straight = 0
        invert = 0.9
        factor = 0.1

        if parent_area_key in area_dictionary.keys():
            areas = bpy.context.screen.areas
            outside_area = None
            sub_area = None

            for area in areas:
                if area.as_pointer() == area_dictionary[parent_area_key]:
                    sub_area = area
                    break

            if sub_area != None:
                for area in areas:
                    area_pointer = area.as_pointer()
                    pointer_list = [sub_area.as_pointer(), parent_area_pointer]

                    width_check = (area.width == sub_area.width)
                    height_check = (area.height == sub_area.height)

                    if self.direction == "RIGHT":
                        split_direction = "HORIZONTAL"
                        sub_area_right_edge_x = (sub_area.x + sub_area.width)
                        edge_delta = (area.x - sub_area_right_edge_x)
                        if area_pointer not in pointer_list and height_check and 10 > edge_delta > -10:
                            outside_area = area

                            for i, area in enumerate(areas):
                                if area == outside_area:
                                    outside_area_index = i

                            for i, area in enumerate(areas):
                                if area.width == outside_area.width:
                                    if i < outside_area_index:
                                        if area.y > outside_area.y:
                                            factor = straight
                                        else:
                                            factor = invert
                                        break

                    elif self.direction == "LEFT":
                        split_direction = "HORIZONTAL"
                        area_right_edge_x = (area.x + area.width)
                        edge_delta = (sub_area.x - area_right_edge_x)
                        if area_pointer not in pointer_list and height_check and 10 > edge_delta > -10:
                            outside_area = area

                            for i, area in enumerate(areas):
                                if area == outside_area:
                                    outside_area_index = i

                            for i, area in enumerate(areas):
                                if area.width == outside_area.width:
                                    if i < outside_area_index:
                                        if area.x > outside_area.x:
                                            factor = straight
                                        else:
                                            factor = invert
                                        break

                    elif self.direction == "TOP":
                        split_direction = "VERTICAL"
                        sub_area_top_edge_y = (sub_area.y + sub_area.height)
                        edge_delta = (area.y - sub_area_top_edge_y)
                        if area_pointer not in pointer_list and width_check and 10 > edge_delta > -10:
                            outside_area = area

                            for i, area in enumerate(areas):
                                if area == outside_area:
                                    outside_area_index = i

                            for i, area in enumerate(areas):
                                if area.height == outside_area.height:
                                    if i < outside_area_index:
                                        if area.y > outside_area.y:
                                            factor = straight
                                        else:
                                            factor = invert
                                        break

                    elif self.direction == "BOTTOM":
                        split_direction = "VERTICAL"
                        area_top_edge_y = (area.y + area.height)
                        edge_delta = (sub_area.y - area_top_edge_y)
                        if area_pointer not in pointer_list and width_check and 10 > edge_delta > -10:
                            outside_area = area

                            for i, area in enumerate(areas):
                                if area == outside_area:
                                    outside_area_index = i

                            for i, area in enumerate(areas):
                                if area.height == outside_area.height:
                                    if i < outside_area_index:
                                        if area.y > outside_area.y:
                                            factor = straight
                                        else:
                                            factor = invert
                                        break

            if outside_area != None and outside_area.as_pointer() not in area_dictionary.values():
                existing_areas = []
                existing_areas.clear()

                # Saving a list of existing areas
                for area in areas:
                    existing_areas.append(area)

                with bpy.context.temp_override(
                    area=outside_area,
                ):

                    bpy.ops.screen.area_split(direction=split_direction, factor=factor)

                with bpy.context.temp_override(
                    area=sub_area,
                ):
                    bpy.ops.screen.area_close()

                for area in areas:
                    if area not in existing_areas:
                        dummy = area
                        with bpy.context.temp_override(
                            area=dummy,
                        ):
                            bpy.ops.screen.area_close()
                        break

            elif sub_area != None:
                with bpy.context.temp_override(
                    area=sub_area,
                ):
                    bpy.ops.screen.area_close()

                # bpy.ops.screen.area_close({"area": area})

                # Splitting outer areas when the height or width of the sub area is not the same as parent
                # Partially works but sometimes makes Blender to crash

                """
                split_outer_areas = False
                parent_area = bpy.context.area
                width_check = (sub_area.width == parent_area.width)
                height_check = (sub_area.height == parent_area.height)

                for i, area in enumerate(areas):
                    if area == parent_area:
                        parent_area_index = i

                if self.direction == "RIGHT" and not height_check:
                    for i, area in enumerate(areas):
                        if i < parent_area_index:
                            sub_area_right_edge_x = (sub_area.x + sub_area.width)
                            edge_delta = (area.x - sub_area_right_edge_x)
                            if 10 > edge_delta > -10:
                                print("Right outer adjacent exists")
                                outer_area = area
                                split_direction = "HORIZONTAL"
                                factor = 0.4
                                split_outer_areas = True
                                break

                if split_outer_areas:
                    existing_areas = []
                    existing_areas.clear()

                    # Saving a list of existing areas
                    for area in areas:
                        existing_areas.append(area)

                    with bpy.context.temp_override(
                        area=outer_area,
                    ):
                        bpy.ops.screen.area_split(direction=split_direction, factor=factor)

                    with bpy.context.temp_override(
                        area=sub_area,
                    ):
                        bpy.ops.screen.area_close()

                    for area in areas:
                        if area not in existing_areas:
                            dummy = area
                            with bpy.context.temp_override(
                                area=dummy,
                            ):
                                bpy.ops.screen.area_close()
                            break
                """

            del area_dictionary[parent_area_key]

        return {"FINISHED"}


class SAT_OT_PIE_tiling_ui_main_call(Operator):
    bl_idname = "sat.tiling_ui_main_call"
    bl_label = "SAT Pie Menu Caller"

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_PIE_tiling_ui_main")
        return {"FINISHED"}


classes = (
    SAT_OT_split_area,
    SAT_OT_close_area,
    SAT_OT_PIE_tiling_ui_main_call,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    _add_hotkey()


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    _remove_hotkey()
