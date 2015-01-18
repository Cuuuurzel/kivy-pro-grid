import sys
sys.path.append( '..' )

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import *
from kivy.uix.floatlayout import FloatLayout

from random import choice, randint 

#from forms.recordform import RecordForm
from progrid import ProGrid, ProGridCustomizator

class TestApp( App ) :
    
    def build( self ) :

        names = 'Federico', 'Mirco', 'Mario', 'Luigi', 'Martin', 'Laura'
        surnames = 'Curzel', 'Rossi', 'Bianchi', 'Corona', 'Brambilla', 'Vettore'
        births = [ '%0.2d/%0.2d/%0.4d'%( randint(1,31), randint(1,12), randint(1940,2000) ) for i in range(0,100) ]

        data = [ { 'name':choice(names), 'surname':choice(surnames), 'birth':choice(births) } for i in range(0,100) ]
        headers     = { 'name':'Nome', 'surname':'Cognome', 'birth':'Data di nascita' }
        columns     = [ 'surname', 'name', 'birth' ]
        row_filters = { 'name':lambda n: n.startswith('M') } 
        row_sorting = [ ['surname','asc'] ]
    
        grid = ProGrid( 
            headers=headers, data=data, columns=columns, \
            row_filters=row_filters, row_sorting=row_sorting, \
            size_hint=(1,1), pos=(0,0)
        )

        btn = ProGridCustomizator( 
            grid=grid, size=(10,10), pos=(100,100) 
        )

        self.t = FloatLayout( size_hint=(1,1) )
        self.t.add_widget( grid )
        self.t.add_widget( btn )
        return self.t

if __name__ == '__main__':
    TestApp().run()



