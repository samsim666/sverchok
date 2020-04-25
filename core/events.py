# This file is part of project Sverchok. It's copyrighted by the contributors
# recorded in the version control history of the file, available from
# its original location https://github.com/nortikin/sverchok/commit/master
#
# SPDX-License-Identifier: GPL3
# License-Filename: LICENSE

"""
Purpose of this module is centralization of update events.

For now it can be used in debug mode for understanding which event method are triggered by Blender
during evaluation of Python code.

Details: https://github.com/nortikin/sverchok/issues/3077
"""


from enum import Enum, auto
from typing import NamedTuple, Union, List
from itertools import takewhile

from bpy.types import Node, NodeTree

from sverchok.utils.context_managers import sv_preferences


class BlenderEvents(Enum):
    tree_update = auto()  # this updates is calling last with exception of creating new node
    monad_tree_update = auto()
    node_update = auto()  # it can be called last during creation new node event
    add_node = auto()   # it is called first in update wave
    copy_node = auto()  # it is called first in update wave
    free_node = auto()  # it is called first in update wave
    add_link_to_node = auto()  # it can detects only manually created links
    node_property_update = auto()  # can be in correct in current implementation
    undo = auto()  # changes in tree does not call any other update events

    def print(self, updated_element=None):
        event_name = f"EVENT: {self.name: <30}"
        if updated_element is not None:
            element_data = f"IN: {updated_element.bl_idname: <25} INSTANCE: {updated_element.name: <25}"
        else:
            element_data = ""
        print(event_name + element_data)


class SverchokEvents(Enum):
    add_node = auto()
    copy_nodes = auto()
    free_nodes = auto()
    node_property_update = auto()
    node_link_update = auto()
    undo = auto()
    undefined = auto()  # most likely this event will responsible for checking links changes

    def print(self, updated_elements: list = None):
        event_name = f"SVERCHOK EVENT: {self.name: <21}"
        if updated_elements is not None:
            element_data = f"NODES: {', '.join([el.name for el in updated_elements]): <25}"
        else:
            element_data = ""
        print(event_name + element_data)


EVENT_CONVERSION = {
    BlenderEvents.tree_update: SverchokEvents.undefined,
    BlenderEvents.monad_tree_update: SverchokEvents.undefined,
    BlenderEvents.node_update: SverchokEvents.undefined,
    BlenderEvents.add_node: SverchokEvents.add_node,
    BlenderEvents.copy_node: SverchokEvents.copy_nodes,
    BlenderEvents.free_node: SverchokEvents.free_nodes,
    BlenderEvents.add_link_to_node: SverchokEvents.node_link_update,
    BlenderEvents.node_property_update: SverchokEvents.node_property_update,
    BlenderEvents.undo: SverchokEvents.undo
}


class Event(NamedTuple):
    type: BlenderEvents
    updated_element: Union[Node, NodeTree, None]

    def get_sverchok_type_event(self):
        try:
            return EVENT_CONVERSION[self.type]
        except KeyError:
            raise KeyError(f"For Blender event type={self.type} Sverchek event is undefined")

    def __eq__(self, other):
        return self.type == other


class CurrentEvents:
    events_wave: List[Event] = []

    @classmethod
    def new_event(cls, event_type: BlenderEvents, updated_element=None):
        if event_type == BlenderEvents.node_update:
            # such updates are not informative
            return
        cls.events_wave.append(Event(event_type, updated_element))
        if cls.is_in_debug_mode():
            event_type.print(updated_element)
        if cls.is_wave_end():
            cls.convert_wave_to_sverchok_event()
            cls.events_wave.clear()

    @classmethod
    def is_wave_end(cls):
        # it is not correct now but should be when this module will get control over the update events
        sign_of_wave_end = [BlenderEvents.tree_update, BlenderEvents.node_property_update,
                            BlenderEvents.monad_tree_update]
        return True if cls.events_wave[-1] in sign_of_wave_end else False

    @classmethod
    def convert_wave_to_sverchok_event(cls):
        sverchok_event_type = cls.events_wave[0].get_sverchok_type_event()
        if cls.is_in_debug_mode():
            if sverchok_event_type == SverchokEvents.undefined:
                sverchok_event_type.print()
            else:
                all_events_of_such_type = takewhile(lambda ev: ev == cls.events_wave[0], cls.events_wave)
                sverchok_event_type.print([ev.updated_element for ev in all_events_of_such_type])

    @staticmethod
    def is_in_debug_mode():
        with sv_preferences() as prefs:
            return prefs.log_level == "DEBUG"
