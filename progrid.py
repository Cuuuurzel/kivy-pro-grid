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
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.listview import ListItemButton, ListView
from kivy.uix.selectableview import SelectableView
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput

from random import random
import time

from flatui.flatui import FlatButton, FlatTextInput, FlatPopup, FloatingAction

Builder.load_file( 'progrid.kv' )

"""
Inspired by DevExpress CxGrid...

-- Features --

    - Rows filtering
    - Rows sorting
    - Rows grouping ( not yet )
    - Columns filtering 
    - Columns sorting
    - Allows end-user to customize the view    

-- Issues --

    - Still damn slow
    - Cannot show more than ~2500 rows due to performance
    - Rows grouping not yet implemented
    - Not saving user configuration

"""
class ProGrid( BoxLayout ) :

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
    content_background_color = ListProperty( [ .95, .95, .95, 1 ] )
    content_font_name = StringProperty( '' ) #'font/Roboto-Light.ttf' )
    content_font_size = NumericProperty( 15 )
    content_align = OptionProperty( 'left', options=['left','center','right'] )
    content_padding_x = NumericProperty( -5 )
    content_padding_y = NumericProperty( None )

    """
    Header properties...
    """
    header = ObjectProperty( None )
    header_background_color = ListProperty( [ .8, .8, .8, 1 ] )
    header_font_name = StringProperty( '' ) #'font/Roboto-Medium.ttf' )
    header_font_size = NumericProperty( 16 )
    header_height = NumericProperty( 40 )
    header_align = OptionProperty( 'left', options=['left','center','right'] )
    header_padding_x = NumericProperty( None )
    header_padding_y = NumericProperty( None )

    """
    Footer properties...
    """
    footer = ObjectProperty( None )
    footer_background_color = ListProperty( [ .8, .8, .8, 1 ] )
    footer_height = NumericProperty( 15 )
    footer_align = OptionProperty( 'left', options=['left','center','right'] )
    footer_padding_x = NumericProperty( None )
    footer_padding_y = NumericProperty( None )

    """
    Other properties of less interest...
    """
    text_color = ListProperty( [ 0, 0, 0, .9 ] )
    grid_color = ListProperty( [ .8, .8, .8, 1 ] )
    grid_width = NumericProperty( 1 )
    row_height = NumericProperty( 28 )

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
        self.bind( columns=self._render )
        self.bind( row_filters=self._render )
        self.bind( row_sorting=self._render )
        self.bind( data_len_limit=self._render )
        self.bind( content_font_size=lambda o,v: self.setter('row_height')(o,v*2) )

        #Binding occurs after init, so we need to force first setup
        self._render( self.data )

    """
    Will re-render the grid.
    """
    def _render( self, *args ) :

        if len( self.data ) > self.data_len_limit : 
            self._raise_too_much_data( len( self.data ) )

        self._setup_data( self.data )

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
        txt_align = {'halign'   :self.header_align    } if self.header_align     else {}
        padding_x = {'padding_x':self.header_padding_x} if self.header_padding_x else {}
        padding_y = {'padding_y':self.header_padding_x} if self.header_padding_x else {}

        args = {}
        args.update( txt_align )
        args.update( font_name )
        args.update( padding_x )
        args.update( padding_y )

        for column in self.columns :
            lbl = Label( 
                text=self.headers[column], color=self.text_color, \
                font_size=self.header_font_size, \
                **args
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
        b = BoxLayout( height=self.row_height, orientation='horizontal', spacing=1 )

        font_name = {'font_name':self.content_font_name} if self.content_font_name else {}
        txt_align = {'halign'   :self.header_align    } if self.header_align     else {}
        padding_x = {'padding_x':self.content_padding_x} if self.content_padding_x else {}
        padding_y = {'padding_y':self.content_padding_x} if self.content_padding_x else {}

        args = {}
        args.update( txt_align )
        args.update( font_name )
        args.update( padding_x )
        args.update( padding_y )

        for column in self.columns :
            lbl = GridLabel( 
                text=line[column], color=self.text_color, \
                font_size=self.content_font_size, \
                **args
            )
            b.add_widget( lbl )

        return b

    """
    Will filter and order data rows.
    """
    def _setup_data( self, data ) :
        
        self._data = []

        if len( data ) > 0 :

            #Data used by customizator
            self._all_columns = sorted( data[0].keys() )

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
Label with background color.
"""
class GridLabel( Label ) :

    background_color = ListProperty( [ .95, .95, .95, 1 ] )

    def __init__( self, **kargs ) : 
        super( GridLabel, self ).__init__( **kargs )


"""
Put this on your form to allow the user customize the ProGrid.
"""
class ProGridCustomizator( FloatingAction ) :
    
    """
    String properties to be translated eventually.
    """       
    popup_title = StringProperty( 'Customize your grid' )     
    hint_filter = StringProperty( 'No filter' )
    how_to_filter = StringProperty( """Write any text to filter rows, for example : 'ar', will match 'ARon', 'mARio' and so on.
You can also use operators, like '> 15' or '== "Mario"'.""" )

    """
    Grid reference.
    """
    grid = ObjectProperty( None )

    """
    Popup reference.
    """
    popup = ObjectProperty( None )

    def __init__( self, **kargs ) :
        super( ProGridCustomizator, self ).__init__( **kargs )

        if not 'grid' in kargs.keys() :
            raise ValueError( 'You need to provide a pointer to your grid using the "grid" parameter.' )
        else : self.grid = kargs['grid']

    """
    Will exit customizer without commit changes.
    """
    def exit_customizer( self, *args ) :
        self.popup.dismiss()

    """
    Will save changes, reaload the grid and dismiss popup.
    """
    def save_and_exit( self, *args ) :

        columns = []
        for column in self.grid._all_columns :
            chk, lbl, fil = self._columns[ column ]
            if chk.active :
                columns.append( column )
        self.grid.columns = columns

        self.exit_customizer()

    """
    Show customization panel.
    """
    def customize( self ) :
        self.popup = FlatPopup( 
            size_hint=(.8,.8), \
            title=self.popup_title, \
            title_size=20, \
            title_color=[0,0,0,.8], \
            content=self._build_content()
        )
        self.popup.open()

    """
    Will build popup content footer.
    """
    def _build_footer( self ) :

        footer = BoxLayout( orientation='horizontal', spacing=10, size_hint=(1,.2) )        
        args = { 'size_hint':(.2,1), 'background_color':[0,.59,.53,1], 'background_color_down':[0,.41,.36,1] }
        footer.add_widget( Label( text=self.how_to_filter, color=[0,0,0,.8], font_size=11 ) )
        
        cancel_button = FlatButton( text='X', **args )
        cancel_button.bind( on_press=self.exit_customizer )

        ok_button = FlatButton( text='OK', **args )
        ok_button.bind( on_press=self.save_and_exit )

        footer.add_widget( cancel_button )
        footer.add_widget( ok_button )
        return footer

    """
    Will build a single popup content row.
    """
    def _build_content_row( self, column ) :

        row = BoxLayout( orientation='horizontal', size_hint=(1,None), height=30 )
        chk = CheckBox( active=( column in self.grid.columns ) )
        fil = FlatTextInput( text='', hint_text=self.hint_filter, multiline=False, valign='middle' )
        lbl = Label( text=self.grid.headers[column], color=[0,0,0,.8], halign='left', valign='middle' )
        lbl.bind( size=lbl.setter('text_size') )
   
        row.add_widget( chk )
        row.add_widget( lbl )
        row.add_widget( fil )
        return row, chk, lbl, fil 

    """
    Will build popup content.
    """
    def _build_content( self ) :
        x = BoxLayout( orientation='vertical', padding=[5,5,5,10])
        content = BoxLayout( orientation='vertical', margin=10 )

        self._columns = {}
        
        for column in self.grid._all_columns :
            row, chk, lbl, fil = self._build_content_row( column ) 
            content.add_widget( row )
            self._columns[ column ] = chk, lbl, fil

        x.add_widget( content )
        x.add_widget( BoxLayout( size_hint=(1,1) )   )
        x.add_widget( self._build_footer() )

        return x























