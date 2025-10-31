#    Copyright © 2021 Andrei Puchko
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


from q2gui import q2style


class Q2Style(q2style.Q2Style):
    def _windows_style(self):
        focusable_controls_list = [
            "q2line",
            "q2check",
            "q2text",
            "q2button",
            "q2radio",
            "q2lookup",
            "q2combo",
            "q2toolbutton",
            "q2progressbar",
            "q2grid",
            "q2sheet",
            "q2date",
            "q2tab",
            "q2list",
            "QToolButton",
            "q2spin",
            "q2doublespin",
            "q2time",
            "QTabBar::tab",
            "QRadioButton",
            "#radio",
        ]
        focusable_controls = ", ".join(focusable_controls_list)
        focusable_controls_with_focus = ", ".join(["%s:focus" % x for x in focusable_controls_list])
        focusable_controls_with_readonly = ", ".join(
            ['%s[readOnly="true"]' % x for x in focusable_controls_list]
        )
        style = (
            """
                QFrame, q2frame {{
                    color:{color};
                    background-color:{background};
                    margin:0px;
                    padding:0px;
                    {border_radius}
                }}
                %(focusable_controls)s
                    {{
                        color:{color};
                        background-color:{background_control};
                        margin:{margin};
                        padding:{padding};
                        selection-color: {color_selection};
                        selection-background-color : {background_selection};
                        border: {border};
                        {border_radius}
                    }}
                %(focusable_controls_with_readonly)s
                    {{
                        color:{color_disabled};
                    }}

                %(focusable_controls_with_focus)s
                    {{
                        color:{color_focus};
                        background-color:{background_focus};
                        border: {border_focus};
                    }}
                QTabBar::tab:selected, QTabBar::tab:selected:disabled
                    {{
                        color: {color_focus};
                        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                           stop: 0 {background_selected_item}
                                           stop: 0.9 {background_selected_item}
                                           stop: 1 {background}
                                    );
                        border-bottom: None;
                        min-height:1.2em;
                    }}
                QTabBar::tab:focus
                    {{
                        background-color: {background_focus};
                    }}
                QRadioButton
                    {{
                        border: none;
                        padding:0px 0.3em;
                    }}

                QRadioButton:checked {{
                        color: {color_focus};
                        background-color: {background_selected_item};
                }}

                QRadioButton:focus
                    {{
                        background-color: {background_focus};
                    }}

                q2spin {{border:{border};}}

                QTabBar::tab
                    {{
                        padding:0.4em 0.3em;
                        margin: 0 1px 0 0;
                        border-bottom-right-radius: 0;
                        border-bottom-left-radius: 0;
                    }}

                q2tab::pane{{
                    background:{background_selected_item};
                    border: {border};
                    margin: 0 0 0.3em;
                    {border_radius}
                }}

                q2label{{
                    color:{color};
                    background: transparent;
                }}
                QGroupBox#title
                    {{
                        border: {border};
                        margin: 0.5em 0em;
                        padding: 0.5em 0.3em 0.1em 0.3em;
                    }}
                QGroupBox::title {{
                        subcontrol-origin: padding;
                        font: bold;
                        left: 1em;
                        top: -{font_size}px;
                }}
                QMdiSubWindow, QMainWindow
                    {{
                        color: {color};
                        background-color: {background};
                    }}

                QMenuBar
                    {{
                        color: {color};
                        background-color: {background_control};
                        border: None;
                        {border_radius}
                    }}

                QMenuBar::item:selected
                , QMenu::item:selected
                    {{
                        color: {color_selection};
                        background-color: {background_menu_selection};
                    }}

                QToolButton
                {{
                    color: black;
                    background-color: {toolbutton_background};
                    border: None;
                    {border_radius}
                    margin: 0px 0.1em;
                    padding-bottom: 0.1em;
                    border: 1px solid gray;
                }}

                QToolButton:hover
                    , QTabBar::tab:hover
                    , q2button:hover
                    , q2list::item:hover
                    , q2combo::item:selected
                    , QRadioButton:hover
                    {{
                        color: black;
                        background-color: {background_menu_selection};
                    }}

                QToolButton::menu-indicator
                    {{
                        subcontrol-origin: relative ;
                        subcontrol-position: center bottom;
                        bottom:  -0.7ex;
                        left:  0.1ex;
                        color: green;
                    }}
                q2button
                    {{
                        border:{border};
                        padding: 0.3em 0.5em;
                    }}

                q2space
                    {{
                        background:transparent;
                        border:none;
                    }}

                QToolBar {{background-color:transparent; padding: 0px; border:0px solid black;}}
                QToolBar:disabled {{background-color:transparent; padding: 0px; border:0px solid black;}}

                #main_tab_widget::tab-bar
                    {{
                        alignment: center;
                    }}

                #main_tab_bar::tab:last
                    {{
                        color:white;
                        background:green;
                        font-weight:bold;
                        width: 2em;
                    }}
                #main_tab_bar::tab:last:hover
                    {{
                        color:green;
                        background:white;
                        max-height: 1em;
                    }}
                QSplitter
                    {{
                        height:2px;
                        width:2px;
                    }}
                QSplitter:handle
                    {{
                        border-left: 1px dotted {color};
                        border-top: 1px dotted {color};
                    }}
                QSplitter:handle::pressed
                    {{
                        border-left: 1px solid  {color};
                        border-top: 1px solid {color};
                    }}
                *:disabled
                    {{
                        color: {color_disabled};
                        background: {background_disabled};
                    }}

                q2combo QAbstractItemView
                    {{
                        color: {color_focus};
                        background:{background_focus};
                    }}
                QListView::item:selected
                    {{
                        color: {color_focus};
                        background-color: {background_selected_item};
                    }}
                QTableView
                    {{
                    alternate-background-color:{background_control};
                    background-color:{background};
                    gridline-color: gray;
                    }}

                QHeaderView::section, QTableView:focus
                    {{
                        color:{color};
                        background-color:{background};
                    }}

                QTableView:item::selected
                    {{
                        color: {color_focus};
                        background-color:{background_focus};
                    }}

                QTableView QTableCornerButton::section,
                QTableWidget QTableCornerButton::section
                    {{
                        background-color:{background_control};
                        border:none;
                    }}

                #radio:focus
                    {{
                        background:{background_focus};
                    }}

                QHeaderView::section
                    {{
                        color:{color};
                        background-color:{background_disabled};
                        border: 1px solid gray;
                    }}

/*                QToolButton
                    {{
                        min-height: 1.2em;
                        min-width: 1.2em;
                    }}*/

                #radio, q2check
                    {{
                        border:1px solid palette(Mid);
                        {border_radius}

                    }}
                #mdiarea {{border:none;}}
                q2check
                    {{
                        padding: 0em  0.3ex
                    }}
                q2text
                    {{
                        margin:0em;
                    }}

                QMenu{{
                    border:1px solid {color};
                }}
                QMenu::separator {{
                    height: 1px;
                    background: {color};
                }}

                QMenu::item, QMenu:disabled
                    {{
                        color: black;
                        background-color: {toolbutton_background};
                        selection-color: palette(HighlightedText);
                        selection-background-color: {background_menu_selection};
                    }}
                QMenu::item:disabled
                    {{
                        color: gray;
                    }}

                QProgressBar
                    {{
                        text-align: center;
                        {border_radius}
                    }}
                QProgressBar::chunk {{
                    background-color: {background_selected_item};
                }}
                QCalendarWidget QAbstractItemView
                    {{
                        color:{color};
                    }}
                q2button#_cancel_button, q2button#_ok_button
                    {{
                        margin: 0.4ex 1ex;
                        min-width: 8ex;
                        border: {border};
                    }}
                q2button#_ok_button
                    {{
                        background-color:lightgreen;
                        color:black;
                    }}
                q2button#_ok_button:focus {{background-color:green;color:white}}
                q2button#_ok_button:hover {{background-color:LightSeaGreen}}
                q2button#_ok_button:disabled {{background-color:{background_disabled}}}
                q2label {{border:0px;margin: 0px}}
                QListView {{padding:0.3em 0.1em}}
                QComboBox {{padding:0ex 0.1em;margin-right:0.3em;}}
                QComboBox  QListView {{margin-right:0.3em;}}

                QMdiSubWindow:title {{height: 1.5em}}
                QFrame:disabled,QGroupBox:disabled {{background-color:transparent}}

                QTabWidget::pane {{ top: -1px;}}
                QTabBar::tab:disabled, QTabWidget::pane:disabled
                    {{
                        background-color:{background_disabled}
                    }}
                QTabBar:disabled {{background:transparent}}
                QTabBar {{qproperty-drawBase: 0;}}
                QTabBar::tab:!selected {{margin-top: 2px;}}
                q2text[readOnly="true"]
                    {{
                        color:black;
                        background-color:rgb(194, 206, 219);
                    }}
                q2frame#grb {{margin:2px}}
                QToolButton#qt_toolbar_ext_button {{background:cyan}}
                QToolButton#tab_bar_close_button:hover {{background:tomato}}
            """
            % locals()
        )
        return style

    def _mac_style(self):
        return self._windows_style()

    def _linux_style(self):
        return self._windows_style()
