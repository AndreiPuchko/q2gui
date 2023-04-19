import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()


from q2gui import q2style


class Q2Style(q2style.Q2Style):
    def _dark_style(self):
        return """
                * {{
                    color: {color};
                    background-color: {background};
                    border: 1px solid {border};

                }}

                *:disabled {{color: {color_disabled};}}

                QAbstractButton, QTabBar:tab, QLineEdit, QComboBox:!editable
                    {{
                        background-color: {background_control};
                        selection-color: {color_selection};
                        selection-background-color : {background_selection};
                    }}
                    
                QTabBar:tab
                    {{
                        padding-left: 0.4em;
                        padding-right: 0.4em;
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

                QTabWidget::pane
                    {{
                        border: 1px solid {background_selected_item};
                    }}

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

                """

    def _light_style(self):
        return self._dark_style()
