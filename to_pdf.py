from fpdf import FPDF
import os
from time import strftime, localtime

class PdfRaport(FPDF):
    colors={'maccent':[255,255,255]}

    #def __init__(self,*args,**kwargs):
        #super(FPDF, self).__init__(*args,**kwargs)
        #font_path = r'H:\backUp_pcwiek\prywante\Programming\projects\site-markup\DejaVuSans.ttf'
        #self.add_font('DeJaVu', '', font_path, uni=True) 
        
    def adjustable_header(self,big=False):
        # Arial bold 15
        font_s = 15 if big else 10
        self.set_font('Arial', 'B', font_s)
        # Calculate width of title and position
        w = 0
        if not big:
            w = self.get_string_width(self.title) + 6
            self.set_x((self.fw - w) / 2)
        # Colors of frame, background and text
        #self.set_draw_color(0, 80, 180)
        self.set_fill_color(230, 230, 0)
        self.set_text_color(220, 50, 50)
        # Thickness of frame (1 mm)
        #self.set_line_width(1)
        # Title
        self.cell(w, 9, self.title, 0, 0, 'C')
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Text color in gray
        self.set_text_color(128)
        # Page number
        self.cell(25, 10, strftime("%Y-%m-%d %H:%M", localtime()), 0, 0, align='L')
        self.cell(0, 10, 'Page ' + str(self.page_no()) + ' / {nb}', 0, 0, align='C')
        self.set_font('Arial', 'I', 6)
        self.cell(0, 10, 'exported from simplynail-site-markup',0,10,align='R')

    def chapter_title(self, num, label):
        font_h=12
        bar_h = 6
        circle_ext=6

        number = str(num)
        w = max(self.get_string_width(number),bar_h)+circle_ext

        self.ln(circle_ext/2)
        self.set_font('Arial', '', font_h)
        self.set_fill_color(255,176,156)
        self.set_text_color(255, 255, 255)
        # Title
        self.set_x(self.l_margin+w/2)
        self.cell(w/2, bar_h, ' ', 0, 0, 'L', 1)
        self.set_fill_color(255,176,156)
        self.cell(0, bar_h, ' %s' % (label), 0, 0, 'L', 1)

        self.set_font('Arial', 'B', font_h)
        # Colors of frame, background and text
        self.set_draw_color(255, 255, 255)
        self.set_fill_color(255, 0, 0)
        self.set_text_color(255, 255, 255)

        self.set_x(self.l_margin)
        self.ellipse(self.x, self.y-circle_ext/2, w, w, 'F')
        self.set_fill_color(200, 22, 255)
        self.cell(w, bar_h, number, 0, 1, 'C', 0)
        # Line break
        self.ln(circle_ext)

    def chapter_body(self, img, description):
        remaining_lines_no = [4]
        if description != None:
            desc_lines = [10,10,1]
            remaining_lines_no.extend(desc_lines)
        w = self.w - (self.l_margin + self.r_margin)
        h = self.h - self.y - sum(remaining_lines_no) - 15 - self.b_margin
        self.image(img,w=w,h=h)
        self.ln(remaining_lines_no[0])
        if description != None:
            # Times 12
            self.set_font('Times', '', 12)
            self.set_text_color(0, 0, 0)
            # Output justified text
            self.set_font('', 'B')
            self.cell(0, remaining_lines_no[1], 'Description:')
            # Line break
            self.ln(remaining_lines_no[2])
            self.set_font('', '')
            self.multi_cell(0, 5, description,align='T')
            # Line break
            self.ln(remaining_lines_no[3])

    def add_marker(self, num, title, description, img):
        self.add_page()
        self.adjustable_header()
        self.chapter_title(num, title)
        self.chapter_body(img, description)

    def add_cover(self,project_overview,map_path):
        """

        :rtype: object
        """
        self.add_page('L')
        self.adjustable_header(big=True)

        self.set_font('Times', '', 12)
        self.set_text_color(0, 0, 0)
        # Output justified text
        self.set_font('', 'B')
        self.cell(0, 5, 'Overview:')
        # Line break
        self.ln()
        self.set_font('', '')
        self.multi_cell(0, 5, project_overview)
        self.ln(2)

        w = self.w - (self.l_margin + self.r_margin)
        h = self.h - self.y - self.b_margin
        self.image(map_path, h=h)
    
    def init_report(self,cwd, title='',author='',cover=None,markers=[]):
        self.cwd = cwd
        self.set_title(title)
        self.set_author(author)
        self.cover = cover
        self.markers = markers
        
    def setup_pdf(self,with_description=True):
        import os
        self.alias_nb_pages()
        if self.cover != None:
            img_path = os.path.join(self.cwd,*self.cover['image_path'].split('/'))
            print(img_path)
            self.add_cover(self.cover['overview'],img_path)
        if self.markers != []:
            for marker in self.markers:
                if with_description:
                    description = marker['description']
                else:
                    description = None
                img_path = os.path.join(self.cwd,*marker['image_path'].split('/'))
                self.add_marker(marker['belly_text'],marker['name'],description=description,img=img_path)   
        
    def print_pdf(self,path):
        self.output(path, 'F')

if __name__ == "__main__":
    cwd = os.path.curdir
    print(cwd)

    pdf = PdfRaport()
    pdf.alias_nb_pages()
    pdf.set_title("My Title")
    pdf.set_author('Ny name')

    pdf.add_cover('Project overview',r'C:\Users\pawel\OneDrive\Dokumenty\python_Projects\site-markup\site-markup\_przykladowy\map.jpg')
    pdf.add_marker(1,'first','first descr',
                   r'C:\Users\pawel\OneDrive\Dokumenty\python_Projects\site-markup\site-markup\_przykladowy\photos\20161120_140706.jpg')
    pdf.add_marker(1, 'second', 'second descr',
                   r'C:\Users\pawel\OneDrive\Dokumenty\python_Projects\site-markup\site-markup\_przykladowy\photos\20161120_140757.jpg')
    pdf.output(os.path.join(cwd,'tuto3.pdf'), 'F')