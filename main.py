from __future__ import print_function, with_statement, division
import os
from functools import partial

import tiny_orm

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.logger import Logger as logging
import kivy.metrics as kvmetrics

from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.uix.behaviors.button import ButtonBehavior

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from kivy.properties import StringProperty
from kivy.properties import ListProperty
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.properties import BooleanProperty
# colors: background, bellyButton main color, marker fill, marker outer ring
GUI_COLORS = [(35, 76, 99), (55, 153, 86), (255, 200, 91), (255, 200, 91)]
for no,item in enumerate(GUI_COLORS):
    GUI_COLORS[no] = (item[0]/255.0, item[1] / 255.0, item[2] / 255.0, 1)

if os.name == 'posix':
    #from camera import AndroidCamera as Camera
    from new_camera import Camera as NewCamera
else:
    from new_emulate_camera import EmulateCamera as NewCamera

kivy_lang = '''
<IntroScreen>:
    orientation: 'vertical'
    BoxLayout:
        id: found_projects
        orientation: 'vertical'
    BellyButton:
        belly_text: "+"
        on_press: root.create_new_project()
        belly_pos: [root.center_x,root.center_y]

<NewProject>:
    orientation: 'vertical'
    Label:
        font_size: sp(app.gui_multiplier)
        text: "New project's name:"
        text_size: self.size
    TextInput:
        id: project_name
    Label:
        id: hint
        font_size: sp(app.gui_multiplier)
        text: 'Now create map reference to further mark it up. Press on "+" button to create project and take a photo of the map'
        text_size: self.size
    BellyButton:
        id: new_project_add
        #size: (self.size[0]*2,self.size[1]*2)
        belly_text: "+"
        on_press: root.add_project()

<MarkerEditForm>:
    orientation: 'vertical'
    BoxLayout:
        orientation: 'horizontal'
        BellyButton:
            id: marker_number
        Label:
            font_size: sp(app.gui_multiplier)*1.5
            text: "Edit marker data"
            size: self.texture_size
            text_size: self.size
    ImageButton:
        id:imgbutton
        width: self.ids.img.width
#        image_path: root.marker.image_path
    Label:
        font_size: sp(app.gui_multiplier)
        text: "Name:"
        size: self.texture_size
        text_size: self.size
        size_hint_y: None
        canvas.before:
            Color:
                rgba: (1,0,0,1)
            Rectangle:
                size: self.size
                pos: self.pos
    TextInput:
        id: marker_name
        multiline: False
        font_size: sp(app.gui_multiplier)
        size_hint_y: None
        height: self.minimum_height
    Label:
        font_size: sp(app.gui_multiplier)
        text: 'Description:'
        size: self.texture_size
        text_size: self.size
        size_hint_y: None
        canvas.before:
            Color:
                rgba: (1,0,0,1)
            Rectangle:
                size: self.size
                pos: self.pos
    TextInput:
        id: marker_description
        font_size: sp(app.gui_multiplier)
    BoxLayout:
        orientation: 'horizontal'
        BellyButton:
            #size: (self.size[0]*2,self.size[1]*2)
            belly_text: "+"
            on_press: root.describe_marker()
        BellyButton:
            #size: (self.size[0]*2,self.size[1]*2)
            belly_text: "del"
            on_press: pass
        BellyButton:
            #size: (self.size[0]*2,self.size[1]*2)
            belly_text: "x"
            on_press: root.parent.open_project()

<ProjectMap>:
    BoxLayout:
        id: main_box
    BellyButton:
        id: add_photo
        belly_pos: (root.size[0]-self.size[0]/2,root.y+self.size[1]/2)
        belly_text: "+"
        on_press: root.add_marker()

<MapScatter>:
    scatter_pos: imgscatter.pos
    scatter_scale: imgscatter.scale
    image_border: max(*self.ids.img.size)/100
#    canvas.after:
#        Color:
#            rgba: 1, 0, 0, 0.5
#        Rectangle:
#            size: self.size
#            pos: self.pos
    Scatter:
        id: imgscatter
        size_hint: None, None
        size: img.size
        auto_bring_to_front: False
        do_rotation: False
#        on_scale: root.scatter_scale = self.scale
#        on_pos: root.scatter_pos = self.pos
#        canvas.after:
#            Color:
#                rgba: 0, 1, 0, 0.5
#            Rectangle:
#                size: self.size
#                pos: self.pos
        Image:
            id: img
            source: root.image_path
#            pos: imgscatter.pos
            size: self.texture_size
            canvas.before:
                Color:
                    rgba: 1,1,1,1
                BorderImage:
                    border: (root.image_border,root.image_border,root.image_border,root.image_border)
                    size: (self.width+2*root.image_border,self.height+2*root.image_border)
                    pos: (-1*root.image_border,-1*root.image_border)

<ImagePopupFrame>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            id:box
        Button:
            size_hint_y: None
            height: 50
            text: "Close"
            on_release: root.dismiss()

<ImageButton>:
    Image:
        id: img
        source: root.image_path
        height: root.height
        #width: root.width
        allow_stretch: True
        #keep_ratio: False
        #size: self.texture_size
        #center: root.center
        pos:root.pos


<BellyButton>:
    size_hint: None, None
    size: (belly_label.texture_size[1]*1.2, belly_label.texture_size[1]*1.2)
    center: self.belly_pos
    canvas.after:
        Color:
            rgba: 0,1,0,1
        Line:
            points: self.x, self.y, self.x+10, self.y+10

    canvas:
        Color:
            rgba: self.belly_color
        Ellipse:
            pos: self.pos
            size: self.size
        Line:
            points: self.x, self.y, self.belly_pos[0], self.belly_pos[1]
    Label:
        id: belly_label
        size: self.texture_size
        font_size: sp(app.gui_multiplier)
        pos: [root.center_x-self.size[0]/2,root.center_y-self.size[1]/2]
        text: root.belly_text

<Marker>:
    canvas.before:
        Color:
            rgba: app.GUI_COLORS[3]
        Rectangle:
            size: self.size[0]/2,self.size[1]/2
            pos: self.pos
        Color:
            rgba: app.GUI_COLORS[2]
        Ellipse:
            pos: self.pos[0]-3,self.pos[1]-3
            size: self.size[0]+6, self.size[1]+6

'''
# <BELOW> just for reference
"""
kivy_lang = '''
<MainWidget>:
    on_my_property: my_label.text = 'from button bind method via StringProperty' + self.my_property

    Label:
        id: my_label
        text: root.my_property
    BellyButton:

    Button:
        id: my_button
        text: 'intro button'
'''
class MainWidget(BoxLayout):
    # bind some properties
    my_property = StringProperty('0')

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
    #     if needed to do sth on widget construction
        self.ids.my_button.bind(on_press=self.my_method)


    def my_method(self,*args,**kwargs):
        self.my_property = str(int(self.my_property)+1)
        self.ids.my_button.text = 'new'
"""
# </BELOW> #######################

"""
class MyCamera(Camera):
    def __init__(self,folder_path,filename='',**kwargs):
        Camera.__init__(self,**kwargs)
        self.folder_path = folder_path
        self.filename = filename

    def new_photo_path(self,folder_path,filename):
        import os.path
        if filename == '':
            from time import localtime, strftime
            filename = strftime("%Y%m%d_%H%M%S", localtime())
        return os.path.join(folder_path, filename + '.png')

    def take_shot(self):
        self.image_path = self.new_photo_path(self.folder_path, self.filename)
        self.filename = ''
        return self._take_picture(self.on_success_shot, self.image_path)

    def on_success_shot(self, loaded_image_path):
        # image_str = self.image_convert_base64
        return self.image_path

    # converting image to a base64, if you want to send it, for example, via POST:
    def image_convert_base64(self):
        with open(self.image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        if not encoded_string:
            encoded_string = ''
        return encoded_string
"""

class ImagePopup(Popup):
    image_path = StringProperty()

class ImageButton(ButtonBehavior, Widget):
    image_path = StringProperty()
    #
    # def __init__(self,image_path,title, *args,**kwargs):
    #     super(ImageButton, self).__init__(*args, **kwargs)
    #     self.image_path = image_path
    #     content = MapScatter(image_path)
    #     self.popup = Popup(title = title, content = content)
    #     #self.bind(on_press=self.popup.open)
    #
    # def show_popup(self):
    #     self.popup.open()

class BellyButton(ButtonBehavior, Widget):
    belly_pos = ListProperty([0,0])
    belly_text = StringProperty('#')
    belly_color = ListProperty(GUI_COLORS[1])

    def __init__(self, *args, **kwargs):
        #print('data received to BellyButton init: ', kwargs)
        super(BellyButton, self).__init__(*args,**kwargs)
        #kwargs['belly_pos'] = self.belly_pos
        #kwargs['belly_text'] = self.belly_text

    def on_press(self):
        print('pressed ' + self.belly_text)

class Marker(BellyButton,tiny_orm.Model):
    db_columns = ['db_id','name','description','image_path','location','belly_text']
    name = ''
    description = ''
    location = [0,0]
    image_path = ''

    def __init__(self, *args, **kwargs):
        #print('received to Marker constructor:',kwargs)
        # first inherit from Kivy, then from other stuff(like tinyORM) or app will crash
        # so that Kivy's __init__ runs first (and I think sets up the properties that ORM writes to)
        super(Marker, self).__init__(*args,**kwargs)
        #self.pos = self.location


    '''@property
    def location(self):
        return self.belly_pos

    @property
    def number(self):
        return self.belly_text'''

    def old_update_pos(self, scatter_offset, img_offset, scale):
#        self.belly_pos = [scatter_offset[0] + (img_offset[0] - self.location[0]) * scale,
#                          scatter_offset[1] + (img_offset[1] - self.location[1]) * scale]
        self.belly_pos = [img_offset[0] + self.location[0] * scale,
                          img_offset[1] + self.location[1] * scale]
        return self.belly_pos

    def old_save_pos(self,scatter_offset, img_offset, scale):
        self.location = [ (self.location[0] - img_offset[0]) / scale, (self.location[1] - img_offset[1]) / scale]
        return self.location

    def update_pos(self, offset, scale, scatterMap):
        self.belly_pos = [offset[0] + self.size[0] / 2 + (self.location[0]) * scale,
                          offset[1] + self.size[1] / 2 + (self.location[1]) * scale]
        logging.info('''info: updated belly_pos context::
        current scatter pos: {}
        current scatter scale: {}
        saved marker location: {}
        calculated belly_pos: {}'''.format(offset, scale, self.location, self.belly_pos))
        return self.belly_pos

    def save_pos(self,offset,scale):
        self.location = [(self.location[0] - offset[0]) / scale, (self.location[1] - offset[1]) / scale]
        return self.location

    def remove_photo(self,photo_path):
        # remove photo from folder
        pass

    def remove_maker(self):
        # remove from db
        # remove photo
        pass
class ImagePopupFrame(BoxLayout):
    pass

class MarkerEditForm(BoxLayout):

    def __init__(self,marker,*args,**kwargs):
        super(MarkerEditForm,self).__init__(*args,**kwargs)
        self.marker = marker
        content = ImagePopupFrame()
        content.ids.box.add_widget(MapScatter(self.marker.image_path))
        content.ids.box.children[0].scatter_pos = content.ids.box.center
        self.popup = Popup(title = self.marker.belly_text + ': ' + self.marker.name, content = content)
        self.ids.imgbutton.image_path = self.marker.image_path
        self.ids.imgbutton.bind(on_press=self.popup.open)
        self.ids.marker_number.belly_text = self.marker.belly_text
        self.ids.marker_name.text = self.marker.name
        self.ids.marker_description.text = self.marker.description

    def describe_marker(self):
        print('describing')
        #print(self.marker,self.marker.__dir__())
        if not hasattr(self.marker, 'db_id'):
            query = tiny_orm.Manager(Marker)
            all_markers = query.all()
            if all_markers == []:
                last_number = 0
            else:
                numbers = [0]
                for marker in all_markers:
                    numbers.append(int(marker.belly_text))
                last_number = max(numbers)
            self.marker.belly_text = str(last_number + 1)

        self.marker.name = self.ids.marker_name.text
        self.marker.description = self.ids.marker_description.text

        self.marker.save()
        self.parent.open_project()

class Gui(BoxLayout):
    # app main frame
    def __init__(self,*args,**kwargs):
        BoxLayout.__init__(self,**kwargs)
        Window.clearcolor = GUI_COLORS[0]
        intro = IntroScreen()
        self.add_widget(intro)

    def open_project(self):
        self.clear_widgets()
        self.add_widget(ProjectMap())


class NewProject(BoxLayout):

    def add_project(self):
        project_name = self.ids.project_name.text
        project_path = os.path.join(app.path_app, project_name.replace(' ', '').lower())
        if os.path.exists(project_path):
            self.ids.hint.text = 'This project name is already in use. New name needs to be unique'
        else:
            photos_folderpath = os.path.join(project_path,'photos')
            os.makedirs(photos_folderpath)
            print(project_path)
            app.camera = NewCamera(project_path)
            app.camera.take_shot('map')
            self.clock = Clock.schedule_interval(partial(self.project_created, project_path),0.5)

    def project_created(self,project_path,*args):
        if app.camera.shot_taken:
            # func to create new db
            self.clock.cancel()
            app.path_project = project_path
            parent=self.parent
            parent.open_project()


class IntroScreen(BoxLayout):
    def __init__(self,*args,**kwargs):
        BoxLayout.__init__(self,**kwargs)
        found_projects = [fn for fn in next(os.walk(app.path_app))[1]]
        for project in found_projects:
            proj_btn = Button(text=project)
            temp_func = partial(self.open_existing,project)
            proj_btn.bind(on_press=temp_func)
            self.ids.found_projects.add_widget(proj_btn)

        if found_projects == []:
            label = Label(text='No existing projects were found. Press on "+" button to create new project')
            self.ids.found_projects.add_widget(label)

    def create_new_project(self):
        parent = self.parent
        self.parent.clear_widgets()
        parent.add_widget(NewProject())

    def open_existing(self,project_name,*args):
        project_path = os.path.join(app.path_app, project_name.replace(' ', '').lower())
        app.path_project = project_path
        self.parent.open_project()

class ProjectMap(FloatLayout):

    def __init__(self,*args,**kwargs):
        FloatLayout.__init__(self,**kwargs)
        app.camera = NewCamera(os.path.join(app.path_project, 'photos'))
        app.path_db = os.path.join(app.path_project,'db.json')
        tiny_orm.Model.define_db(app.path_db)
        self.load_map(self.get_markers())

    def get_markers(self):
        markers = []
        query = tiny_orm.Manager(Marker)
        markers = query.all()
        if len(markers) >= 1:
            for item in markers:
                print('created Marker atributtes: ',item)
                print('marker.belly_pos: ',item.belly_pos)
        return markers

    def load_map(self,markers,**kwargs):
        #self.ids.main_box.clear_widgets()
        self.current_map = MapScatter(os.path.join(app.path_project, 'map.jpg'))
        for marker in markers:
            marker.bind(on_press=partial(self.show_marker_dialog, marker))
            self.current_map.add_widget(marker)
#            self.current_map.ids.imgscatter.add_widget(marker)
        self.current_map.bind(scatter_pos=self.transfer_pos)
        self.current_map.bind(scatter_scale=self.transfer_pos)
#        self.current_map.bind(scatter_scale=self.scale_makers)

        self.ids.main_box.add_widget(self.current_map)

        img_bigger_dim = self.current_map.ids.img.texture_size.index(max(self.current_map.ids.img.texture_size))
        print(img_bigger_dim)
        self.current_map.ids.imgscatter.scale = 0.9 * Window.size[img_bigger_dim] / self.current_map.ids.imgscatter.size[0]
        self.current_map.ids.imgscatter.scale_min = 0.5 * self.current_map.ids.imgscatter.scale
        self.current_map.ids.imgscatter.center = (Window.size[0]/2,Window.size[1]/2)

#    def transfer_pos(self, *args, **kwargs):
        # maybe just add the markers to Scatter directly and on_scale change/update/(decrease by scale) the size of the marker so it stays the same size on screen?
        # TODO move this method to ScatterMap and bind in KVlang with on_scatter_pos and on_scatter_scale
#        for no in range(0,len(self.current_map.children)-1):
#            self.current_map.children[no].update_pos(self.current_map.scatter_pos,self.current_map.scatter_scale)
            #self.belly_pos = self.current_map.children[no].save_pos(self.current_map.scatter_pos,self.current_map.scatter_scale)
#
    def transfer_pos(self, *args, **kwargs):
        for no in range(0,len(self.current_map.children)-1):
            #pass
            self.current_map.children[no].update_pos(self.current_map.scatter_pos,self.current_map.scatter_scale, self.current_map)
            #self.belly_pos = self.current_map.children[no].save_pos(self.current_map.scatter_pos,self.current_map.scatter_scale)

    def add_marker(self,*args,**kwargs):
        app.camera.take_shot()
        self.clock = Clock.schedule_interval(self.photo_taken,0.5)

    def photo_taken(self,*args,**kwargs):
        logging.info('info:in photo taken funct')
        logging.info('info:cam photo path= %r'% app.camera.image_path)

        if app.camera.shot_taken:
            logging.info('info:in photo taken funct and shot taken True')
            self.clock.cancel()
            self.new_marker = Marker()
            self.new_marker.image_path = app.camera.image_path
            self.place_marker_hint()

    def place_marker_hint(self,*args,**kwargs):
        marker_hint = BellyButton()
        #marker_hint.belly_color[2] = marker_hint.belly_color[2] * 0.5
        marker_hint.belly_color[3] = 0.5
        marker_hint.belly_pos = self.center
        marker_hint.bind(on_press=partial(self.show_marker_dialog,self.new_marker))
        self.add_widget(marker_hint)

        # deactivate/remove "+" button just for now
        # or change it to "x" = delete/cancel
        self.remove_widget(self.ids.add_photo)

    def calc_new_maker_pos(self,marker):
        marker.location = self.center
        #self.new_marker.save_pos(self.current_map.scatter_pos,self.current_map.scatter_scale)
        marker.save_pos(self.current_map.scatter_pos,self.current_map.scatter_scale)
        logging.info('''info: marker saved location context::
        current window center: {}
        current window scatterMap scatter_pos: {}
        current window scatterMap scatter_scale: {}
        current scatterMap scatter size: {}
        current scatterMap img size: {}
        marker size: {}
        saved marker location: {}
        calculated new Marker belly_pos(its center): {}
        '''. format(self.center, self.current_map.scatter_pos, self.current_map.scatter_scale, self.current_map.ids.imgscatter.size, self.current_map.ids.img.size, self.new_marker.size, self.new_marker.location, self.new_marker.belly_pos ))

    def show_marker_dialog(self,marker,*args,**kwargs):
        if marker.belly_text == '#':
            self.calc_new_maker_pos(marker)
        parent = self.parent
        self.parent.clear_widgets()
        print(parent)
        parent.add_widget(MarkerEditForm(marker))
        # self.ids.main_box.clear_widgets()
        # self.ids.main_box.add_widget(MarkerEditForm())


class MapScatter(FloatLayout):
    image_path = StringProperty('')
    scatter_pos = ListProperty()
    scatter_scale = NumericProperty(1.0)
    image_border = NumericProperty(1.0)

    def __init__(self, map_path,*args,**kwargs):
        FloatLayout.__init__(self,*args,**kwargs)
        self.image_path = map_path
        #self.image_border = kvmetrics.sp(app.gui_multiplier)*0.5


class MyApp(App):
    gui_multiplier = NumericProperty(30)
    path_app = ''
    path_db = ''
    path_project = StringProperty('')
    camera = ObjectProperty(None)
    GUI_COLORS = GUI_COLORS

    def build(self):
        Builder.load_string(kivy_lang)
        return Gui()

    def on_pause(self):
        return True

if __name__ == '__main__':
    app = MyApp()

    tiny_orm.Model.tables = [Marker]

    if os.name == 'posix':
        app.path_app = '/sdcard/documents/site-markup'
    else:
        app.path_app = os.path.join(os.getcwd(), 'site-markup')
    if not os.path.exists(app.path_app):
        os.makedirs(app.path_app)
    print(app.path_app)
    app.run()