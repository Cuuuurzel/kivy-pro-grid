# -*- coding: utf-8 -*-
import pdb
import sys

from functools import partial
from kivy.adapters.dictadapter import DictAdapter
from kivy.adapters.listadapter import ListAdapter
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.metrics import dp, sp
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

import pdb 

from material_ui.flatui.flatui import FlatButton, FlatTextInput, FloatingAction
from material_ui.flatui.labels import BindedLabel, ResizeableLabel
from material_ui.flatui.layouts import ColorBoxLayout
from material_ui.flatui.popups import AlertPopup, FlatPopup, OkButtonPopup

#KV Lang files
from pkg_resources import resource_filename
path = resource_filename( __name__, 'progrid.kv' )
Builder.load_file( path )

#Icons
icon_settings_32 = resource_filename( __name__, 'images/settings-32.png' )

"""
Inspired by DevExpress CxGrid...

-- Features --

    - Rows filtering
    - Rows sorting
    - Columns filtering 
    - Columns sorting
    - Allows end-user to customize the view    

-- Future implementations --

    - Allow end-user to sort rows
    - Allow end-user to sort columns
    - Rows grouping

-- Issues --

    - Still damn slow
    - Rows grouping not yet implemented
    - Not saving user configuration
    - Columns all have the same width by default

"""
class ProGrid( BoxLayout ) :

    """
    Data to display, array of dictionaries.
    """
    data = ListProperty( [] )

    """
    Label for any column.
    """
    headers = DictProperty( {} )

    """
    List of columns to show.
    """
    columns = ListProperty( [] )

    """
    List of ALL possibile columns, ordered.
    """
    col_order = ListProperty( [] )

    """
    Dictionary containing functions used to filter data.
    """
    row_filters = DictProperty( {} )

    """
    Dictionary containing the strings the user will read if costumizing the grid,
    """
    row_filters_names = DictProperty( {} )

    """
    If true touch are not passed down to single widgets.
    """
    records_readonly = BooleanProperty( True )

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
    If you need to bypass this limit, just update this value.
    Default is 2000.
    """
    data_len_limit = NumericProperty( 1000 )

    """
    Use this to force cast on every column.
    """ 
    coltypes = DictProperty( {} ) 

    """
    Text displayed if no data is provided
    """ 
    text_no_data = StringProperty( 'No data found.' ) 

    """
    Content properties...
    """
    content = ObjectProperty( None )
    selection_color = ListProperty( [ .6, .6, 1, 1 ] )
    content_background_color = ListProperty( [ .98, .98, .98, 1 ] )
    content_font_name = StringProperty( '' ) 
    content_font_size = NumericProperty( dp(15) )
    content_align = OptionProperty( 'left', options=['left','center','right'] )

    """
    Header properties...
    """
    header = ObjectProperty( None )
    header_background_color = ListProperty( [ .93, .93, .93, 1 ] )
    header_font_name = StringProperty( '' )
    header_font_size = NumericProperty( dp(17) )
    header_height = NumericProperty( dp(52) )
    header_align = OptionProperty( 'left', options=['left','center','right'] )

    """
    Footer properties...
    """
    footer = ObjectProperty( None )
    footer_background_color = ListProperty( [ .93, .93, .93, 1 ] )
    footer_height = NumericProperty( dp(30) )
    footer_align = OptionProperty( 'left', options=['left','center','right'] )

    """
    Other properties of less interest...
    """
    text_color = ListProperty( [ 0, 0, 0, .9 ] )
    grid_color = ListProperty( [ .93, .93, .93, 1 ] )
    grid_width_h = NumericProperty( dp(1) )
    grid_width_v = NumericProperty( dp(0) )
    row_height = NumericProperty( dp(42) )

    """
    Touch callbacks
    """
    on_double_tap = ObjectProperty( None )
    on_long_press = ObjectProperty( None )
    on_select = ObjectProperty( None )

    """
    Private stuffs...
    """
    _data = ListProperty( [] )
    _rows = ListProperty( [] ) 
    _coltypes = DictProperty( {} )


    def __init__( self, **kargs ) :

        super( ProGrid, self ).__init__( **kargs )
        self.___grid = {}

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
        self._build_coltypes()
        
        for col in self.columns : self.___grid[col] = []

        #Header & footer
        self._gen_header()
        self._gen_footer()

        #Content
        self.content.clear_widgets()
        self.content.height = 0
        self._rows = []

        for n, line in enumerate( self._data ) :
            row = self._gen_row( line, n )
            self._rows.append( row )
            self.content.add_widget( row )
            self.content.height += row.height
        
    """
    Called whenever a row is selected.
    """
    def on_row_select( self, n ) :
        if self.on_select : self.on_select( n, self._data[n] )
        
    """
    Called whenever a row is double tapped.
    """
    def on_row_double_tap( self, n ) :
        if self.on_double_tap : self.on_double_tap( n, self._data[n] )
        
    """
    Called whenever a row is pressed of a long time.
    """
    def on_row_long_press( self, n ) :
        if self.on_long_press : self.on_long_press( n, self._data[n] )

    """
    Will add columns names to header.
    """
    def _gen_header( self ) :
        self.header.clear_widgets()
        args = self._build_header_args()
        first_col = True

        for column in self.columns :

            spacing = u'  ' if first_col else u''
            text    = spacing + self.headers[column] 
            text    = text.encode( 'utf-8' )

            lbl     = ColumnHeader( text=text, meta=column, **args )

            first_col = False
            self.header.add_widget( lbl )
            self.___grid[column].append( lbl )

    """
    Will prepare footer layout.
    This view will allow to quickly remove filters.
    """
    def _gen_footer( self ) :
        pass

    """
    Will generate a single row.
    """
    def _gen_row( self, line, n ) :

        b = RowLayout( 
            height=self.row_height, 
            orientation='horizontal', 
            rowid=n, grid=self, 
            spacing=[self.grid_width_h, self.grid_width_v],
        )
        args = self._build_content_args()
        
        first_col = True
        for column in self.columns :

            val = self._coltypes[column]( 
                line[column] if column in line.keys() else '' 
            )

            if self._coltypes[column] == bool :
                w = ColorBoxLayout( background_color=self.content_background_color )
                c = CheckBox( active=val, size_hint=(None,1), width=sp(32), **args )
                s = BoxLayout( size_hint=(1,1) )
                w.add_widget( c )
                w.add_widget( s )
            else : 
                spacing = u'  ' if first_col else u''
                text = spacing + val if val not in ['None', u'None'] else u''
                text = text.encode( 'utf-8' )
                w = BindedLabel( text=text, **args )

            b.add_widget( w )
            first_col = False
            self.___grid[column].append( w )

        return b

    """
    Will filter and order data rows.
    """
    def _setup_data( self, data ) :
        
        if len(self.col_order) == 0 :
            self.col_order = self.columns

        self._data = []
        if len( data ) > 0 :

            #Data used by customizator
            self._all_columns = self.data[0].keys()           

            #Filtering
            self._data = filter( self._validate_line, data )

            #Sorting
            if len( self.row_sorting ) > 0 :
                field, mode = self.row_sorting[0]
                reverse = False if mode == 'asc' else True
                self._data = sorted( self._data, key=lambda o: o[field], reverse=reverse )
        else :
            self.add_widget( Label( text=self.text_no_data, color=self.text_color ) )
         
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
    Returns a single dictionary using dict.update().
    """
    def _build_dict( self, *args ) :
        result = {}
        for d in args : result.update( d )
        return result

    """
    Args passed down to headers labels.
    """
    def _build_header_args( self ) :
        font_name   = {'font_name'  :self.header_font_name} if self.header_font_name else {}
        font_size   = {'font_size'  :self.header_font_size} if self.header_font_size else {}
        h_align     = {'halign'     :self.header_align    } if self.header_align     else {}
        v_align     = {'valign'     :'middle'             }
        color       = {'color'      :self.text_color      } if self.text_color       else {}
        root_layout = {'root_layout':self}
        hover_color = {'hover_color':[0,0,1,.5]}
        grid        = {'grid'       :self}
        return self._build_dict( v_align, h_align, font_name, font_size, color, root_layout, hover_color, grid )

    """
    Args passed down to content labels.
    """
    def _build_content_args( self ) :        
        v_align   = {'valign'    :'middle'}
        font_name = {'font_name' :self.content_font_name} if self.content_font_name else {}
        font_size = {'font_size' :self.content_font_size} if self.content_font_size else {}
        h_align   = {'halign'    :self.content_align    } if self.content_align     else {}
        color     = {'color'     :self.text_color       } if self.text_color        else {}
        b_color   = {'fill_color':self.content_background_color } if self.content_background_color else {}
        return self._build_dict( v_align, h_align, font_name, font_size, color, b_color )#, padding_x, padding_y )

    """
    Called whenever a column is resized.
    """
    def on_column_resize( self, oldsize, newsize, column ) :
        print( oldsize, newsize, column )
        newwidth = newsize[0]
        for widget in self.___grid[column] :
            widget.width = newwidth
            widget.size_hint[0] = None

    """
    Associates to each column the correct data type.
    Uses the first row of data.
    """
    def _build_coltypes( self ) :
    
        columns = ( set(self.headers.keys()) - set(self.coltypes) )
        self._coltypes = self.coltypes

        if len( self._data ) > 0 : 
            line = self._data[0]
        else : line = [ '' for c in columns ]

        for column in columns :

            obj = line[column] if column in line.keys() else ''
            if isinstance( obj, bool ) : 
                self._coltypes[column] = bool
            else : 
                self._coltypes[column] = str
                     
    """
    Will update a single row of the grid.
    """
    def update_single_row( self, rowid, data ) :
        self.data[rowid] = data
        self.content.remove_widget( self._rows[rowid] )
        self._rows[rowid] = self._gen_row( data, rowid )
        self.content.add_widget( self._rows[rowid], len(self.content.children) )


"""
Put this on your form to allow the user customize the ProGrid.

Currently, three kind of filters are supported :

  1) Simple text filter : 'ar' will match 'aron' and 'mario'.

  2) Expressions starting with Python comparison operators.
  Those are checked and evalued using eval.
  For example, '> 14' or '== 0'

  3) Expressions containing '$VAL'.
  Those are checked and evalued using eval.
  For example, '$VAL.startswith( "M" )'.
"""
class ProGridCustomizator( FloatingAction ) :
    
    """
    String properties to be translated eventually.
    """       
    popup_title = StringProperty( 'Customize your grid' )     
    hint_filter = StringProperty( 'No filter' )
    cannot_use_expression_for_field = StringProperty( """
Cannot use filter for field %s.
Press on '?' for more information.
""" )
    filters_help = StringProperty( """
Three kind of filters are supported :

  1) Simple text filter, for example, 'ar' will match 'aron' and 'mario'.

  2) Expressions starting comparison operators ( <, <=, =>, >, == and != ).
  For example, '> 14' or '== 0'.

  3) Expressions containing '$VAL'.
  For example, '$VAL == "M"'.

Please quote ( '' ) any text in your filters.""" )

    """
    Grid reference.
    """
    grid = ObjectProperty( None )

    """
    Popup reference.
    """
    popup = ObjectProperty( None )

    def __init__( self, **kargs ) :
        super( ProGridCustomizator, self ).__init__( 
            icon=icon_settings_32, **kargs 
        )
        self._help_popup = OkButtonPopup( text=self.filters_help )
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
        self._filter_error_occur = False
        self.grid.columns = self._get_columns()
        self.grid.row_filters, self.grid.row_filters_names = self._get_row_filters()
        if not self._filter_error_occur : self.exit_customizer()

    """
    Will return the filters to be applied on the grid content.
    """
    def _get_row_filters( self ) :
        
        filters = {}
        filters_names = {}
        comparators = '< <= => > == != and or'.split(' ')
        startswith = lambda v: expression.startswith(v)

        for column in self._columns.keys() :
 
            chk, lbl, fil = self._columns[ column ]
            if len( fil.text.strip() ) > 0 :

                expression = fil.text.strip()

                if len( list( filter(startswith, comparators) ) ) > 0 :
                    foo = 'lambda VAL: %s' % ( '_format_val(VAL) ' + expression )
                elif '$VAL' in expression :                 
                    foo = 'lambda VAL: %s' % ( expression.replace('$VAL','_format_val(VAL)') )
                else :
                    foo = "lambda VAL: _format_val(VAL) == _format_val('" + expression + "')"

                try :
                    filters[ column ] = eval( foo )
                    filters_names[ column ] = expression
                except Exception as e : 
                    AlertPopup( text=self.cannot_use_expression_for_field % ( lbl.text.lower() ) ).open()
                    self._filter_error_occur = True
                    print( e )

        return filters, filters_names
            

    """
    Will return the ordered list of columns to be shown.
    """
    def _get_columns( self ) :

        columns = []
        for column in self._columns.keys() :            
            chk, lbl, fil = self._columns[ column ]
            if chk.active :
                columns.append( column )
        return sorted( columns, key=lambda o: self.grid.col_order.index(o) )

    """
    Show customization panel.
    """
    def customize( self ) :
        self.popup = FlatPopup( 
            size_hint=(.95,.7), \
            title=self.popup_title, \
            title_size=dp(20), \
            title_color=[0,0,0,.8], \
            content=self._build_content()
        )
        self.popup.open()

    """
    Will build popup content footer.
    """
    def _build_footer( self ) :

        footer = BoxLayout( orientation='horizontal', spacing=dp(10), size_hint=(1,None), height=dp(35) )        
        args = { 'size_hint':(.2,1), 'color':[0,.59,.53,1], 'color_down':[0,0,0,.7] }
        
        txt = '[ref=main][b]       ?       [/b][/ref]'
        lbl = Label( text=txt, markup=True, color=[0,0,0,.8], font_size=dp(18) )
        lbl.bind( on_ref_press=self._help_popup.open )

        cancel_button = FlatButton( markup=True, text='Cancel', **args )
        cancel_button.bind( on_press=self.exit_customizer )

        ok_button = FlatButton( markup=True, text='[b]OK[/b]', **args )
        ok_button.bind( on_press=self.save_and_exit )

        footer.add_widget( lbl )
        footer.add_widget( cancel_button )
        footer.add_widget( ok_button )
        return footer

    """
    Will build a single popup content row.
    """
    def _build_content_row( self, column ) :

        row = BoxLayout( orientation='horizontal', size_hint=(1,None), height=dp(30) )
        chk = CheckBox( active=( column in self.grid.columns ) )

        fil = FlatTextInput( 
            text=self.grid.row_filters_names[column] if column in self.grid.row_filters_names.keys() else '',\
            hint_text=self.hint_filter, multiline=False, valign='middle' 
        )
        lbl = Label( 
            text=self.grid.headers[column],\
            color=[0,0,0,.8], halign='left', valign='middle' 
        )
        lbl.bind( size=lbl.setter('text_size') )
   
        row.add_widget( chk )
        row.add_widget( lbl )
        row.add_widget( fil )
        return row, chk, lbl, fil 

    """
    Will build popup content.
    """
    def _build_content( self ) :

        s = ScrollView()
        x = BoxLayout( orientation='vertical' )#, padding=[dp(5),dp(5),dp(5),dp(10)] )
        content = GridLayout( cols=1, size_hint=(1,None) )
        content.height = 0

        self._columns = {}
        
        for column in sorted( self.grid.headers.keys() ) :
            
            row, chk, lbl, fil = self._build_content_row( column ) 
            content.add_widget( row )
            content.height += row.height
            self._columns[ column ] = chk, lbl, fil
        
        s.add_widget( content )
        x.add_widget( s )
        x.add_widget( self._build_footer() )

        return x

"""
Resizable widget.
"""
class ColumnHeader( ResizeableLabel ) :

    grid = ObjectProperty( None )

    def __init__( self, **kargs ) :
#        kargs['text'] = '[b]' + kargs['text'] + '[/b]'
#        kargs['markup'] = True
        super( ColumnHeader, self ).__init__( **kargs )
        self.on_new_size = self.grid.on_column_resize

"""
Row layout, with tap, double tap and long press callback.
"""
class RowLayout( BoxLayout ) :
    
    rowid = NumericProperty( None )
    grid = ObjectProperty( None )   

    def __init__( self, **kargs ) :
        super( RowLayout, self ).__init__( **kargs )
        
    def _create_clock( self, touch ) :
        Clock.schedule_once( self.on_long_press, .5 )

    def _delete_clock( self, touch ) :
        Clock.unschedule( self.on_long_press )

    def on_long_press( self, time ) :
        if self.grid : self.grid.on_row_long_press( self.rowid )

    def on_touch_down( self, touch ) :
        if touch.is_double_tap : 
            return self.on_double_tap( touch )        
        self._create_clock( touch )
        return self.grid.records_readonly or super(RowLayout,self).on_touch_down(touch)

    def on_touch_up( self, touch ) :
        self._delete_clock( touch )
        if self.grid : self.grid.on_row_select( self.rowid )
        return self.grid.records_readonly or super(RowLayout,self).on_touch_up(touch)

    def on_double_tap( self, touch ) :
        if self.grid : self.grid.on_row_double_tap( self.rowid )
        return self.grid.records_readonly

"""
Used by filters...
"""
def _format_val( v ) : return str(v).lower()









