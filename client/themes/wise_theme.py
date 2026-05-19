class WiseTheme:
    # Colors
    PRIMARY = "#9fe870"           # Wise Green
    PRIMARY_ACTIVE = "#cdffad"    # Wise Green Hover
    PRIMARY_NEUTRAL = "#c5edab"
    PRIMARY_PALE = "#e2f6d5"
    
    CANVAS = "#ffffff"            # Pure White
    CANVAS_SOFT = "#e8ebe6"       # Sage-tinted background
    
    INK = "#0e0f0c"               # Near-black
    INK_DEEP = "#163300"
    BODY = "#454745"              # Secondary body
    MUTE = "#868685"              # Captions
    
    POSITIVE = "#2ead4b"
    NEGATIVE = "#d03238"
    WARNING = "#ffd11a"
    
    # Geometry
    RADIUS_XL = "24px"
    RADIUS_MD = "12px"
    RADIUS_SM = "8px"
    
    @classmethod
    def get_stylesheet(cls):
        return f"""
        QMainWindow, QDialog {{
            background-color: {cls.CANVAS_SOFT};
        }}
        
        QWidget {{
            font-family: 'Inter', 'Segoe UI', sans-serif;
            color: {cls.INK};
            font-size: 14px;
        }}
        
        QPushButton {{
            background-color: {cls.PRIMARY};
            border: none;
            border-radius: {cls.RADIUS_XL};
            padding: 10px 24px;
            font-weight: 600;
            color: {cls.INK};
        }}
        
        QPushButton:hover {{
            background-color: {cls.PRIMARY_ACTIVE};
        }}
        
        QPushButton:pressed {{
            background-color: {cls.PRIMARY_NEUTRAL};
        }}
        
        QLineEdit {{
            background-color: {cls.CANVAS};
            border: 1px solid {cls.INK};
            border-radius: {cls.RADIUS_MD};
            padding: 10px 16px;
            selection-background-color: {cls.PRIMARY};
        }}
        
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        
        QScrollBar:vertical {{
            border: none;
            background: {cls.CANVAS_SOFT};
            width: 8px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {cls.MUTE};
            min-height: 20px;
            border-radius: 4px;
        }}
        
        QFrame#Card {{
            background-color: {cls.CANVAS};
            border-radius: {cls.RADIUS_XL};
        }}
        
        QLabel#Heading {{
            font-weight: 900;
            font-size: 32px;
            color: {cls.INK};
        }}
        
        QLabel#SubHeading {{
            font-weight: 600;
            font-size: 18px;
            color: {cls.BODY};
        }}
        """
