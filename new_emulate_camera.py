# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 16:15:49 2016

@author: pawel.cwiek
"""
import os.path
from PIL import Image, ImageDraw

from kivy.properties import BooleanProperty

# emulate camera

class EmulateCamera(object):
    emulate_success = True

    def __init__(self,folder_path):
        self.folder_path = folder_path
        self.shot_taken=BooleanProperty(False)

    def new_photo_path(self,folder_path,filename):
        if filename == '':
            from time import localtime, strftime
            filename = strftime("%Y%m%d_%H%M%S", localtime())
        #photo_path = (Environment.getExternalStorageDirectory().getPath() + folder_path +'/{}.jpg'.format(filename))
        photo_path = os.path.join(folder_path,'%s.jpg'%(filename))
        return photo_path

    def take_shot(self,filename=''):
        self.shot_taken=False
        if self.emulate_success == False:
            return None

        self.image_path = self.new_photo_path(self.folder_path,filename)
        filename = self.image_path.split(os.sep)[-1]
        print(self.image_path)
        size = (160,100)

        img = Image.new('RGB', size)
        d = ImageDraw.Draw(img)
        d.rectangle(((0,0),size),fill=(0, 77, 0))
        d.text((0,0), filename, fill=(255, 0, 0))
        text_width, text_height = d.textsize(filename)
        img.save(self.image_path, 'jpeg')

        self.shot_taken=True
        return self.image_path