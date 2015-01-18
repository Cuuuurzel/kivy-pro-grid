import sys
sys.path.append( '..' )

import inspect
import json

from kivy.adapters.dictadapter import DictAdapter
from kivy.adapters.listadapter import ListAdapter
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.properties import *
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.listview import ListItemButton, ListView
from kivy.uix.popup import Popup
from kivy.uix.selectableview import SelectableView
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput

from random import random
import time

Builder.load_file( 'progrid.kv' )

"""
Inspired by DevExpress CxGrid...

-- Features --

    - Rows filtering
    - Rows sorting
    - Rows grouping ( not yet )
    - Columns filtering 
    - Columns sorting
    - Allows end-user to costumize the view    

-- Issues --

    - Still damn slow
    - Cannot show more than ~2500 rows due to performance
    - Rows grouping not yet implemented
    - Not saving user configuration

"""
class ProGrid( BoxLayout ) :#FloatLayout ) :

    """
    Data to display, array of dictionaries.
    """
    data = ListProperty( [] )

    """
    GridLabel for any column.
    """
    headers = DictProperty( {} )

    """
    List of columns to show, ordered.
    """
    columns = ListProperty( [] )

    """
    Dictionary containing functions used to filter data.
    """
    row_filters = DictProperty( {} )

    """
    List of sort rules to use.
    Only one rule is accepted in the current implementation.

    Example :

    [ ['surname','asc'], ['name','asc'], ['birth','desc'] ]

    Curzel  Federico    04/08/2014
    Curzel  Federico    01/04/2014
    Rossi   Mario       01/04/2014
    """
    row_sorting = ListProperty( [] )
    
    """
    There still are performance issues...
    If you feed more than this amount of rows, a TooMuchDataException will be thrown.
    If you still want to bypass this limit, just update this value.
    Default is 2000.
    """
    data_len_limit = NumericProperty( 2000 )
 
    """
    Content properties...
    """
    content = ObjectProperty( None )
    content_background_color = ListProperty( [ .93, .93, .93, 1 ] )
    content_font_name = StringProperty( '' ) #'font/Roboto-Light.ttf' )

    """
    Header properties...
    """
    header = ObjectProperty( None )
    header_background_color = ListProperty( [ .8, .8, .8, 1 ] )
    header_font_name = StringProperty( '' ) #'font/Roboto-Medium.ttf' )
    header_height = NumericProperty( 40 )

    """
    Footer properties...
    """
    footer = ObjectProperty( None )
    footer_background_color = ListProperty( [ .8, .8, .8, 1 ] )
    footer_height = NumericProperty( 15 )

    """
    Other properties of less interest...
    """
    text_color = ListProperty( [ 0, 0, 0, .9 ] )
    grid_color = ListProperty( [ .5, .5, .5, 1 ] )
    grid_width = NumericProperty( 1 )
    row_height = NumericProperty( 28 )
    font_size = NumericProperty( 14 )

    """
    Private stuffs...
    """
    _data = ListProperty( [] )


    def __init__( self, **kargs ) :

        super( ProGrid, self ).__init__( **kargs )

        #Basic setup
        ...    
        
        #Bindings...
        self.bind( data=self._render )
        self.bind( font_size=lambda o,v: self.setter('row_height')(o,v*2) )

        #Binding occurs after init, so we need to force first setup
        self._render( self.data )

    """
    Will re-render the grid.
    """
    def _render( self, data ) :

        if len( data ) > self.data_len_limit : 
            self._raise_too_much_data( len( data ) )

        self._setup_data( data )

        #Content
        self.content.clear_widgets()
        self.content.height = 0

        for line in self._data :
            row = self._gen_row( line )
            self.content.add_widget( row )
            self.content.height += row.height

        #Header & footer
        self._gen_header()
        self._gen_footer()
        ...
        
    """
    Will add columns names to header.
    """
    def _gen_header( self ) :

        self.header.clear_widgets()
        font_name = {'font_name':self.header_font_name} if self.header_font_name else {}

        for column in self.columns :
            lbl = Label( 
                text=self.headers[column], color=self.text_color, \
                height=self.header_height, halign='left', \
                font_size=self.font_size, **font_name
            )
            self.header.add_widget( lbl )

    """
    Will prepare footer layout.
    This view will allow to quickly remove filters.
    """
    def _gen_footer( self ) :
        ...

    """
    Will generate a single row.
    """
    def _gen_row( self, line ) :
        b = BoxLayout( height=self.row_height, orientation='horizontal' )
        font_name = {'font_name':self.header_font_name} if self.content_font_name else {}

        for column in self.columns :
            lbl = GridLabel( 
                text=line[column], color=self.text_color, \
                font_size=self.font_size, **font_name
            )
            b.add_widget( lbl )

        return b

    """
    Will filter and order data rows.
    """
    def _setup_data( self, data ) :

        #Filtering
        temp = filter( self._validate_line, data )

        #Sorting
        field, mode = self.row_sorting[0]
        reverse = False if mode == 'asc' else True
        self._data = sorted( temp, key=lambda o: o[field], reverse=reverse )
         
    """
    Will apply given filters.
    """    
    def _validate_line( self, line ) :
        for k in self.row_filters :
            if not self.row_filters[k]( line[k] ) :
                return False
        return True

    """
    Called whenever the data limit is surpassed.
    """
    def _raise_too_much_data( self, n ) :
        msg = """data_len_limit: %d - Len of data feed: %d
You've got this exception because you did feed too much data.
You can bypass this exception by changing the value of the data_len_limit property.
Be aware of performance issues.
""" % ( self.data_len_limit, n )
        raise ValueError( msg )


"""
Put this on your form to allow the user customize the ProGrid.
"""
class ProGridCustomizator( Button ) :#FloatingAction ) :
   
    def __init__( self, **kargs ) :
        if not 'grid' in kargs.keys() :
            raise ValueError( 'You need to provide a pointer to your grid using the "grid" parameter.' )
        else :
            self.grid = kargs['grid']

        super( ProGridCustomizator, self ).__init__( **kargs )


"""
Label with background color.
"""
class GridLabel( Label ) :

    #background_color = ListProperty( [ .93, .93, .93, 1 ] )
    background_color = ListProperty( [ .93, .93, .93, 1 ] )

    def __init__( self, **kargs ) : 
        super( GridLabel, self ).__init__( **kargs )
















