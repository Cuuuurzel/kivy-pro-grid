import sys
sys.path.append( '/home/curzel/Desktop/dev/kivy-material-ui' )

from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import *
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout

from random import choice, randint 

#from forms.recordform import RecordForm
from progrid.progrid import ProGrid, ProGridCustomizator

SIZE = [ Config.getint('graphics', 'width'), Config.getint('graphics', 'height') ]

class TestApp( App ) :
    
    def build( self ) :

        names = 'Federico', 'Mirco', 'Mario', 'Luigi', 'Martin', 'Laura'
        surnames = 'Curzel', 'Rossi', 'Bianchi', 'Corona', 'Brambilla', 'Vettore'
        births = [ '%0.2d/%0.2d/%0.4d'%( randint(1,31), randint(1,12), randint(1940,2000) ) for i in range(0,100) ]
        data = [ { 'name':choice(names), 'surname':choice(surnames), 'birth':choice(births), 'sample':choice([True,False]) } for i in range(0,100) ]
        
        headers     = { 'name':'Nome', 'surname':'Cognome', 'birth':'Data di nascita', 'sample':'Bool sample' }
        columns     = [ 'surname', 'name', 'birth', 'sample' ]
        row_filters = { 'name':lambda n: n.startswith('M') } 
        row_filters_names = { 'name':"Nomi che iniziano con la 'M'" } 
        row_sorting = [ ['surname','asc'] ]
    
        grid = ProGrid( 
            headers=headers, data=data, columns=columns, \
            row_filters=row_filters, row_sorting=row_sorting, \
            size_hint=(1,1), pos=(0,0)
        )


        self.t = FloatLayout( size_hint=(1,1) )#, size=WINDOW_SIZE )
        self.t.add_widget( grid )
        #self.t.add_widget( al )
        ProGridCustomizator( grid=grid ).add_to_bottom_right( self.t )
        return self.t

    def on_pause( self, *args ) : return True

if __name__ == '__main__':
    TestApp().run()



