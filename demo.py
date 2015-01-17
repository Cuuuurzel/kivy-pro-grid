import sys
sys.path.append( '..' )

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import *

#from forms.recordform import RecordForm
from progrid import ProGrid

class TestApp( App ) :
    
    def build( self ) :

        data = [ 
            { 'name':'Federico', 'surname':'Curzel',  'birth':'04/08/1994' }, \
            { 'name':'Mario',    'surname':'Rossi',   'birth':'01/01/2014' }, \
            { 'name':'Mario',    'surname':'Bianchi', 'birth':'02/01/2014' }, \
            { 'name':'Mario',    'surname':'Verdi',   'birth':'03/01/2014' }, \
            { 'name':'Mario',    'surname':'Blu',     'birth':'04/01/2014' }
        ]
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



