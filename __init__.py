# -*- coding: utf-8 -*-
import bpy
import re

from .ui.context_menu_extention import MenuShapeKeyMoveBelowSelect, extended_menu

bl_info = {
    'name'    : 'SHA-KE Tools',
    'category': '3D View',
    'location': '',
    'version' : (1,0,0),
    'blender' : (3,0,0),
    'author'  : 'arch4e'
}

#
# Operator
#
class OpsShapeKeyMoveBelowSelect(bpy.types.Operator):
    bl_idname = 'shake_tools.move_below_selected'
    bl_label  = 'Move Active Shape Key Below Selected Shape Key'

    target: bpy.props.StringProperty()

    # move selected sk below target
    def execute(self, context):
        key_blocks = context.active_object.data.shape_keys.key_blocks
        index_diff = context.object.active_shape_key_index - key_blocks.find(self.target)
        if index_diff > 1:
            type = 'UP'
        elif index_diff < -1:
            type = 'DOWN'
            index_diff -= 1 # magic
        else:
            return {'FINISHED'}

        index_diff = abs(index_diff)
        while index_diff > 1:
            bpy.ops.object.shape_key_move(type=type)
            index_diff -= 1

        return {'FINISHED'}

class OpsShapeKeyAlignByPrefix(bpy.types.Operator):
    bl_idname = 'shake_tools.align_by_prefix'
    bl_label  = 'Align by prefix'

    def execute(self, context):
        key_blocks = context.active_object.data.shape_keys.key_blocks
        prefix_end = {}

        for key_name in [shape_key.name for shape_key in key_blocks]:
            prefix = re.split(r'\.|_', key_name, 1)[0] # <prefix>_<shape key name>
            # update value if prefix is new or contiguous
            if not prefix in prefix_end.keys() \
               or prefix == re.split(r'\.|_', key_blocks[key_blocks.find(key_name) - 1].name, 1)[0]:
                prefix_end[prefix] = key_blocks.find(key_name)

            while key_blocks.find(key_name) >= (prefix_end[prefix] + 2):
                bpy.context.object.active_shape_key_index = key_blocks.find(key_name)
                bpy.ops.object.shape_key_move(type='UP')
                # update prefix_end when the move is complete
                if key_blocks.find(key_name) <= (prefix_end[prefix] + 1):
                    # update all prefix_end after the target prefix
                    for p in prefix_end.keys():
                        if prefix_end[p] >= prefix_end[prefix]:
                            prefix_end[p] += 1

        return {'FINISHED'}

classes = [
    MenuShapeKeyMoveBelowSelect,
    OpsShapeKeyMoveBelowSelect,
    OpsShapeKeyAlignByPrefix
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.MESH_MT_shape_key_context_menu.append(extended_menu)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.MESH_MT_shape_key_context_menu.remove(extended_menu)

if __name__ == '__main__':
    register()
