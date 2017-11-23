'''
Take picture
============
.. author:: Mathieu Virbel <mat@kivy.org>
Little example to demonstrate how to start an Intent, and get the result.
When you use the Android.startActivityForResult(), the result will be dispatched
into onActivityResult. You can catch the event with the android.activity API
from python-for-android project.
If you want to compile it, don't forget to add the CAMERA permission::
    ./build.py --name 'TakePicture' --package org.test.takepicture \
            --permission CAMERA --version 1 \
            --private ~/code/kivy/examples/android/takepicture \
            debug installd
https://github.com/kivy/kivy/blob/master/examples/android/takepicture/main.py
'''

__version__ = '0.1'

import os.path
from jnius import autoclass, cast
from android import activity, mActivity
from kivy.clock import Clock
from kivy.properties import BooleanProperty

from PIL import Image

Intent = autoclass('android.content.Intent')
MediaStore = autoclass('android.provider.MediaStore')
Uri = autoclass('android.net.Uri')
Environment = autoclass('android.os.Environment')


class Camera(object):
    def __init__(self,folder_path):
        activity.bind(on_activity_result=self.on_activity_result)
        self.folder_path = folder_path
        self.shot_taken=BooleanProperty(False)

    def new_photo_path(self,folder_path,filename):
        if filename == '':
            from time import localtime, strftime
            filename = strftime("%Y%m%d_%H%M%S", localtime())
        #photo_path = (Environment.getExternalStorageDirectory().getPath() + folder_path +'/{}.jpg'.format(filename))
        photo_path = (folder_path +'/{}.jpg'.format(filename))
        return photo_path

    def take_shot(self,filename=''):
        self.shot_taken=False
        self.image_path = self.new_photo_path(self.folder_path,filename)
        intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        self.uri = Uri.parse('file://' + self.image_path)
        self.uri = cast('android.os.Parcelable', self.uri)
        intent.putExtra(MediaStore.EXTRA_OUTPUT, self.uri)
        mActivity.startActivityForResult(intent, 0x123)

    def on_activity_result(self, requestCode, resultCode, intent):
        if requestCode == 0x123:
            Clock.schedule_once(self.after_shot, 0)


    def after_shot(self,*args):

        if os.path.exists(self.image_path):
            im = Image.open(self.image_path)
            width, height = im.size
            im.thumbnail((width / 4, height / 4), Image.ANTIALIAS)
            im.save(self.image_path, quality=95)
            self.shot_taken=True