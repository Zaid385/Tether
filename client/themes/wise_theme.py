from shared.constants.style import ColorTokens, RadiusTokens, TypographyTokens, SpacingTokens

class WiseTheme:
    @classmethod
    def get_stylesheet(cls):
        return f"""
        QMainWindow, QDialog {{
            background-color: {ColorTokens.CANVAS_SOFT};
        }}
        
        QWidget {{
            font-family: 'Inter', 'Segoe UI', sans-serif;
            color: {ColorTokens.INK};
            font-size: {TypographyTokens.SIZE_BODY_MD}px;
        }}
        
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        
        QScrollBar:vertical {{
            border: none;
            background: {ColorTokens.CANVAS_SOFT};
            width: 8px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {ColorTokens.MUTE};
            min-height: 20px;
            border-radius: 4px;
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        """
