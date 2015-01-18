import sys
sys.path.append( '..' )

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import *

from random import choice, randint 

#from forms.recordform import RecordForm
from progrid import ProGrid

class TestApp( App ) :
    
    def build( self ) :

        names = 'Federico', 'Mirco', 'Mario', 'Luigi', 'Martin', 'Laura'
        surnames = 'Curzel', 'Rossi', 'Bianchi', 'Corona', 'Brambilla', 'Vettore'
        births = [ '%0.2d/%0.2d/%0.4d'%( randint(1,31), randint(1,12), randint(1940,2000) ) for i in range(0,100) ]

        data = [ { 'name':choice(names), 'surname':choice(surnames), 'birth':choice(births) } for i in range(0,100) ]
        headers     = { 'name':'Nome', 'surname':'Cognome', 'birth':'Data di nascita' }
        columns     = [ 'name', 'surname', 'birth' ]
        row_filters = { 'name':lambda n: n.startswith('M') } 
        row_sorting = [ ['birth','asc'] ]
    
        self.t = ProGrid( 
            headers=headers, data=data, columns=columns, \
            row_filters=row_filters, row_sorting=row_sorting 
        )
        return self.t

if __name__ == '__main__':
    TestApp().run()



