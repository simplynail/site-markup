# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 11:22:52 2017

@author: pawel.cwiek
"""
import os

from to_pdf import PdfRaport
import tiny_orm

class Marker(tiny_orm.Model):
    db_columns = ['db_id','name','description','image_path','location','belly_text']

if __name__ == '__main__':
    path = r'H:\backUp_pcwiek\prywante\Programming\projects\site-markup'
    os.chdir(path)
    
    path_db = r'H:\backUp_pcwiek\prywante\Programming\projects\site-markup\site-markup\campusl2\db.json'
    tiny_orm.Model.tables = [Marker]
    tiny_orm.Model.define_db(path_db)
    
    cover = {'overview':'Ponizsza lista zawiera usterki zgloszone podczas wizyty na obiekcie Koneser bud. J z dnia 2017-02-01',
            'image_path':'/site-markup/campusl2/map.jpg'}
    markers = []
    query = tiny_orm.Manager(Marker)
    markers = query.all()
    for no,marker in enumerate(markers):
        markers[no] = marker.dictify
    
    pdf = PdfRaport()
    pdf.init_report(path,title='Campus Snag list - L2', author='Pawel Cwiek', cover=cover, markers = markers)
    pdf.setup_pdf()
    pdf.print_pdf('campusL2.pdf')