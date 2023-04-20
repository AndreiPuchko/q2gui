import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()


from q2gui import q2style


class Q2Style(q2style.Q2Style):
    def _windows_style(self):
        s1 = """
                * {{
                    color: {color};
                    background-color: {background};
                    margin: {margin};
                }}

                *:disabled {{color: {color_disabled};}}
                /* focusable controls*/
                QAbstractButton, QTabBar, QLineEdit, QComboBox:!editable, QListView, QTextEdit, QSpinBox
                    {{
                        background-color: {background_control};
                        selection-color: {color_selection};
                        selection-background-color : {background_selection};
                    }}

                q2tab::pane
                    {{
                        margin: {margin};
                        border: {border};
                        border-radius: 0.3em;
                    }}

                QTabBar::tab
                    {{
                        margin: {margin};
                        border: None;
                        padding:0.1em 0.3em;
                    }}

                QPushButton, q2date, q2line, QCheckBox, QRadioButton, QListView, QComboBox
                    {{
                        padding: {padding};
                    }}

                QMenu
                    {{
                        color: palette(text);
                        background-color: palette(base);
                        selection-color: palette(highlighttext);
                        selection-background-color: {background_menu_selection};
                    }}

                QMenuBar
                    {{
                        background-color: {background};
                    }}

                QMenuBar::item:selected
                    {{
                        color: {color_selection};
                        background-color: {background_selection};
                    }}

                QListView:selected, QWidget:focus, QTabBar:focus
                    {{
                        background-color: {background_focus};
                        border: {border_focus};
                    }}

                QListView::item:selected
                    {{
                        background-color: {background_selected_item};
                        color: {color_selected_item};
                    }}

                q2relation:focus {{border:none;background-color: {background};}}


                QTabBar::tab:selected, QRadioButton:checked
                    {{
                        background-color: {background_selected_item};
                        color: {color_selected_item};
                        border: none;
                    }}

                QRadioButton:focus
                    {{
                        color: {color}; 
                        background-color: {background_focus};
                    }}

                QLabel {{border:none;}}

                QTableView
                    {{
                    alternate-background-color:{background};
                    }}

                QHeaderView::section, QTableView:focus
                    {{
                        background-color:{background_control};
                    }}

                QTableView:item::selected
                    {{
                        color: {color};
                        background-color:{background_focus};
                    }}

                QTableView QTableCornerButton::section,
                QTableWidget QTableCornerButton::section
                    {{
                        background-color:{background_control}; 
                        border:none;
                    }}

                QSplitter::handle::vertical  {{
                    background-color:
                    qlineargradient(x1: 0.4,
                                    y1: 0,
                                    x2: 0.6,
                                    y2: 0,
                                    stop: 0 white,
                                    stop: 0.5 darkblue,
                                    stop: 1 white);
                                }}

                QSplitter::handle::horizontal  {{
                    background-color: 
                    qlineargradient(x1: 0,
                                    y1: 0.4,
                                    x2: 0,
                                    y2: 0.6,
                                    stop: 0 white,
                                    stop: 0.5 darkblue,
                                    stop: 1 white);}}

                QSplitter::handle:vertical
                    {{
                        height: 0.3ex;
                        width: 0.3ex;
                    }}

                QWidget {{border-radius:0.3em; }}

                #radio
                    {{
                        padding:0.2em; border:1px solid {background_control};
                    }}

                QMdiSubWindow:enabled
                    {{
                        border: {border_window};
                        }}
                #q2form:disabled {{border: 2px solid transparent;}}

                QGroupBox#title
                    {{
                        border: {border};
                        margin-top: 2ex;
                        padding: 2ex;
                    }}
                QGroupBox::title {{
                        subcontrol-origin: margin;
                        font: bold;
                        left: 1em;
                }}

                QLabel {{margin: 0px}}
          
                """
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
            "q2spin",
            "q2doublespin",
            "QTabBar::tab",
            "QRadioButton",
            "#radio",
        ]
        focusable_controls = ", ".join(focusable_controls_list)
        focusable_controls_with_focus = ", ".join(["%s:focus" % x for x in focusable_controls_list])
        focusable_controls_with_disabled = ", ".join(["%s:disabled" % x for x in focusable_controls_list])
        hoverable_controls = "QTabBar::tab:hover "

        s2 = """
                QFrame,q2frame {{
                    background-color:{background};
                }}

                %(focusable_controls)s
                    {{
                        color:{color};
                        background-color:{background_control};

                    }}
                %(focusable_controls_with_focus)s
                    {{
                        background-color:{background_focus};
                        border: {border_focus};
                    }}
                %(focusable_controls_with_disabled)s
                    {{
                        color:{color_disabled};
                    }}
                QRadioButton:checked, QTabBar::tab:selected, QListView::item:selected
                    {{
                        color: {color_selected_item};
                        background-color: {background_selected_item};
                        border: none;
                    }}

                QTabBar::tab
                    {{
                        margin: {margin};
                        padding:0.1em 0.3em;
                    }}
                
                q2label{{
                    color:{color};
                }}
                
                QGroupBox#title
                    {{
                        border: {border};
                        margin-top: 2ex;
                        padding: 2ex;
                    }}
                QGroupBox::title {{
                        subcontrol-origin: margin;
                        color: {color};
                        background-color:{background};
                        font: bold;
                        left: 1em;
                }}
                QMdiSubWindow, QMainWindow
                    {{
                        color: {color};
                        background-color: {background};
                    }}
                QMenuBar, QToolButton
                    {{
                        color: {color};
                        background-color: {background_control};
                    }}

                QMenuBar::item:selected, QToolButton:hover
                    {{
                        color: {color_selection};
                        background-color: {background_selection};
                    }}

            """ % locals()
        return s2

    def _mac_style(self):
        return self._windows_style()

    def _linux_style(self):
        return self._windows_style()
