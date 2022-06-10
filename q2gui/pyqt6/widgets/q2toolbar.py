import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()


from q2gui.q2app import Q2Actions
from q2gui.q2app import GRID_ACTION_TEXT

from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QToolBar,
    QSizePolicy,
    QToolButton,
    QMenu,
)
from PyQt6.QtCore import Qt, QMargins

from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.pyqt6.q2window import q2_align


class q2toolbar(QFrame, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        self.setLayout(QVBoxLayout() if "v" in meta.get("control") else QHBoxLayout())
        # self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)
        self.layout().setAlignment(q2_align["7"])
        self.layout().setSpacing(-1)
        self.layout().setContentsMargins(QMargins(0, 0, 0, 0))
        self.toolBarPanel = QToolBar()
        # self.toolBarPanel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.toolBarPanel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        action_list = []
        if isinstance(meta.get("actions"), Q2Actions):
            action_list.extend(meta.get("actions"))
            actions = meta.get("actions")
        elif isinstance(meta.get("actions"), list):
            for x in meta.get("actions"):
                if isinstance(x, Q2Actions):
                    action_list.extend(x)
            actions = meta.get("actions")[0]

        if action_list is []:
            return

        tool_bar_qt_actions = QMenu()
        cascade_action = {"": tool_bar_qt_actions}

        for action in action_list:
            if action.get("text", "").startswith("/"):
                continue
            worker = action.get("worker", None)
            action_text_list = action["text"].split("|")
            for x in range(len(action_text_list)):
                action_key = "|".join(action_text_list[:x])
                action_text = action_text_list[x]
                if action_text == "-":
                    action["engineAction"] = cascade_action[action_key].addSeparator()
                else:
                    if x + 1 == len(action_text_list):  # real action
                        action["engineAction"] = cascade_action[action_key].addAction(action_text)
                        action["parent_action"] = cascade_action[action_key]
                        action["parent_action_text"] = action_key

                        action["_set_visible_parent_action"] = lambda mode=True, act=action[
                            "parent_action"
                        ]: act.setVisible(mode)

                        action["_set_visible"] = lambda mode=True, act=action["engineAction"]: act.setVisible(
                            mode
                        )
                        action["_set_enabled"] = lambda mode=True, act=action["engineAction"]: act.setEnabled(
                            mode
                        )
                        action["_set_disabled"] = lambda mode=True, act=action[
                            "engineAction"
                        ]: act.setDisabled(mode)
                        action["engineAction"].setToolTip(action.get("mess", ""))
                        action["engineAction"].setStatusTip(action.get("mess", ""))
                        if worker:
                            action["_worker"] = worker
                            action["engineAction"].triggered.connect(worker)
                        elif action.get("child_where") and action.get("child_form"):

                            def getChildForm(action):
                                def rd():
                                    self.meta["form"].show_child_form(action)

                                return rd

                            action["_worker"] = getChildForm(action)
                            action["engineAction"].triggered.connect(getChildForm(action))

                        action["engineAction"].setShortcut(
                            action["hotkey"] if not action["hotkey"] == "Spacebar" else Qt.Key.Key_Space
                        )
                        action["engineAction"].setShortcutContext(
                            Qt.ShortcutContext.WidgetWithChildrenShortcut
                        )
                    else:  # cascade
                        subMenu = "|".join(action_text_list[: x + 1])
                        if subMenu not in cascade_action:
                            cascade_action[subMenu] = cascade_action[action_key].addMenu(
                                f"{action_text}  {'' if '|' in subMenu else '  '}"
                            )

        self.main_button = QToolBar()
        self.main_button_action = QToolButton()
        self.main_button_action.setText(GRID_ACTION_TEXT)
        self.main_button_action.setToolTip(self.meta.get("mess", ""))
        self.main_button_action.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.main_button_action.setMenu(tool_bar_qt_actions)
        self.main_button.addWidget(self.main_button_action)

        self.layout().addWidget(self.main_button)
        if not actions.show_main_button:
            self.main_button.setVisible(False)

        self.toolBarPanel.addSeparator()
        self.toolBarPanel.addActions(tool_bar_qt_actions.actions())
        for x in self.toolBarPanel.actions():
            if hasattr(self.toolBarPanel.widgetForAction(x), "setPopupMode"):
                self.toolBarPanel.widgetForAction(x).setPopupMode(
                    QToolButton.ToolButtonPopupMode.InstantPopup
                )

        if actions.show_actions:
            self.layout().addWidget(self.toolBarPanel)

    def set_context_menu(self, widget):
        widget.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        widget.addActions(self.toolBarPanel.actions())
