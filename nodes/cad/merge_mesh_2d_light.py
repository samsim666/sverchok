# This file is part of project Sverchok. It's copyrighted by the contributors
# recorded in the version control history of the file, available from
# its original location https://github.com/nortikin/sverchok/commit/master
#
# SPDX-License-Identifier: GPL3
# License-Filename: LICENSE


import bpy

from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvMergeMesh2DLight(bpy.types.Node, SverchCustomTreeNode):
    """
    Triggers: Merge 2D mesh into one
    Tooltip: Takes in account intersections and holes

    Has hidden output socket, look N panel
    """
    bl_idname = 'SvMergeMesh2DLight'
    bl_label = 'Merge mesh 2D light'
    bl_icon = 'AUTOMERGE_ON'

    def update_sockets(self, context):
        [self.outputs.remove(sock) for sock in self.outputs[2:]]
        if self.face_index:
            self.outputs.new('SvStringsSocket', 'Face index')
        updateNode(self, context)

    face_index: bpy.props.BoolProperty(name="Show face mask", update=update_sockets,
                                       description="Show output socket of index face mask")
    accuracy: bpy.props.IntProperty(name='Accuracy', update=updateNode, default=5, min=3, max=12,
                                    description='Some errors of the node can be fixed by changing this value')

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, 'face_index', toggle=True)
        layout.prop(self, 'accuracy')

    def sv_init(self, context):
        self.inputs.new('SvVerticesSocket', 'Verts')
        self.inputs.new('SvStringsSocket', "Faces")
        self.outputs.new('SvVerticesSocket', 'Verts')
        self.outputs.new('SvStringsSocket', "Faces")

    def process(self):
        pass


def register():
    bpy.utils.register_class(SvMergeMesh2DLight)


def unregister():
    bpy.utils.unregister_class(SvMergeMesh2DLight)
