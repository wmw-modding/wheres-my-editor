import lxml
from lxml import etree
from PIL import Image, ImageTk
from waltex import getWaltexImage

class Widgets():
    def __init__(this, element : etree.Element, gamePath : str, texturePath : str = None, baseLayoutFile : str = None) -> None:
        this.element = element
        
        this.attributes = this.element.attrib
        
        if not texturePath:
            texturePath = this.attributes['texturePath']
        this.texturePath = texturePath
        
        if not baseLayoutFile:
            baseLayoutFile = this.attributes['baseLayoutFile']
        this.baseLayoutFile = baseLayoutFile
        
        this.gamePath = gamePath
        
        this.widgets = []
        this.comments = []
        
        this.getWidgets()
        
    def getWidgets(this):
        for w in this.element:
            if not isinstance(w, etree.Comment):
                widget = Widget(w, this.texturePath)
                this.widgets.append(widget)
            else:
                this.comments.append(w)
        
    
# main widget class
class Widget():
    """
        Main widget
    """
    def __init__(this, widget : etree.Element, gamePath, texturePath : str) -> None:
        this.widget = widget
        this.attributes = this.widget.attr
        this.name = this.type = this.attributes['type']
        this.gamePath = gamePath
        
        this.pos = (0, 0)
        this.size = (0, 0)
        this.id = 0
        this.layer = 0
        
        this.forceAspect = False
        this.visible = True
        
        this.getValues()
        
    def getValues(this):
        if this.attributes['pos']:
            this.pos = [float(v) for v in tuple(this.attributes['pos'].split(' '))]
        
        if (this.attributes['id']):
            this.id = float(this.attributes['id'])
            
        if (this.attributes['layer']):
            this.layer = float(this.attributes['layer'])
            
        if (this.attributes['size']):
            this.size = [float(v) for v in tuple(this.attributes['size'].split(' '))]
            
        if (this.attributes['forceAspect']):
            this.setForceAspect(this.attributes['forceAspect'])
            
        if (this.attributes['visible']):
            this.visible = bool(this.attributes['visible'])
        
    def setForceAspect(this, aspect = (1,1)):
        if isinstance(aspect, str):
            forceAspect = tuple([float(v) for v in aspect.split(':')])
        elif not aspect:
            forceAspect = False
        else:
            forceAspect = tuple(aspect)
        
        this.forceAspect = forceAspect

# button
class WT_PUSH_BUTTON(Widget):
    """
        Button
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
# label, commonly also used for background
class WT_LABEL(Widget):
    """
        Text Label, commonly also used for background
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
class WT_TOGGLE(Widget):
    """
        Toggle
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
class WT_SLIDER(Widget):
    """
        Slider, used for things like the camera slider in bigger levels
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
class WT_PROGRESS_BAR(Widget):
    """
        Progress bar
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
class WT_GROUP(Widget):
    """
        Group for widgets?
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
class WT_ICON_LIST(Widget):
    """
        Icon list for displaying pictures of levels
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
class WT_SCROLLABLE_CAMERA(Widget):
    """
        Used for scrolling in `SN_MainMenu_v2.xml`
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
class WT_SCROLLABLE_SET(Widget):
    """
        Set that holds world packs
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
# don't know what this is, but it is used in `SN_Editor.xml`
class WT_CANVAS(Widget):
    """
        don't know what this is, but it is used in `SN_Editor.xml`
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
# "finger catcher" for digging events
class WT_FINGER_CATCHER(Widget):
    """
        "finger catcher" for digging events
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        

WidgetTypes = {
    'WT_PUSH_BUTTON': WT_PUSH_BUTTON,
    'WT_LABEL': WT_LABEL,
    'WT_TOGGLE': WT_TOGGLE,
    'WT_SLIDER': WT_SLIDER,
    'WT_PROGRESS_BAR': WT_PROGRESS_BAR,
    'WT_GROUP': WT_GROUP,
    'WT_ICON_LIST': WT_ICON_LIST,
    'WT_SCROLLABLE_CAMERA': WT_SCROLLABLE_CAMERA,
    'WT_SCROLLABLE_SET': WT_SCROLLABLE_SET,
    'WT_CANVAS': WT_CANVAS,
    'WT_FINGER_CATCHER': WT_FINGER_CATCHER,
}

if __name__ == '__main__':
    pass