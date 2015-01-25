import sys
sys.path.append( '..' )

from functools import partial
from kivy.adapters.dictadapter import DictAdapter
from kivy.adapters.listadapter import ListAdapter
from kivy.clock import Clock
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

from flatui.flatui import FlatButton, FlatTextInput, FloatingAction
from flatui.labels import BindedLabel
from flatui.popups import AlertPopup, FlatPopup, OkButtonPopup

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
    - Rows grouping ( not yet )
    - Columns filtering 
    - Columns sorting
    - Allows end-user to customize the view    

-- Issues --

    - Still damn slow
    - Rows grouping not yet implemented
    - Not saving user configuration

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
    List of columns to show, ordered.
    """
    columns = ListProperty( [] )

    """
    Dictionary containing functions used to filter data.
    """
    row_filters = DictProperty( {} )

    """
    Dictionary containing the strings the user will read if costumizing the grid,
    """
    row_filters_names = DictProperty( {} )

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
    selection_color = ListProperty( [ .6, .6, 1, 1 ] )
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
    header_font_size = NumericProperty( 17 )
    header_height = NumericProperty( 50 )
    header_align = OptionProperty( 'center', options=['left','center','right'] )
    header_padding_x = NumericProperty( None )
    header_padding_y = NumericProperty( 0 )# -9 )

    """
    Footer properties...
    """
    footer = ObjectProperty( None )
    footer_background_color = ListProperty( [ .8, .8, .8, 1 ] )
    footer_height = NumericProperty( 20 )
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


    def __init__( self, **kargs ) :

        super( ProGrid, self ).__init__( **kargs )

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

        for n, line in enumerate( self._data ) :
            row = self._gen_row( line, n )
            self.content.add_widget( row )
            self.content.height += row.height

        #Header & footer
        self._gen_header()
        self._gen_footer()
        ...
        
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
        font_name = {'font_name':self.header_font_name} if self.header_font_name else {}
        font_size = {'font_size':self.header_font_size} if self.header_font_size else {}
        h_align   = {'halign'   :self.header_align    } if self.header_align     else {}
        v_align   = {'valign'   :'middle'             }
        color     = {'color'    :self.text_color      } if self.text_color       else {}
        padding_x = {'padding_x':self.header_padding_x} if self.header_padding_x else {}
        padding_y = {'padding_y':self.header_padding_y} if self.header_padding_y else {}

        args = {}
        args.update( font_name )
        args.update( font_size )
        args.update( h_align   )
        args.update( v_align   )
        args.update( color     )
        args.update( padding_x )
        args.update( padding_y )

        for column in self.columns :
            lbl = ColumnHeader( 
                text=self.headers[column], **args
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
    def _gen_row( self, line, n ) :
        b = RowLayout( height=self.row_height, orientation='horizontal', rowid=n, grid=self, spacing=self.grid_width )

        font_name = {'font_name'       :self.content_font_name} if self.content_font_name else {}
        font_size = {'font_size'       :self.content_font_size} if self.content_font_size else {}
        h_align   = {'halign'          :self.content_align    } if self.content_align     else {}
        v_align   = {'valign'          :'middle'}
        color     = {'color'           :self.text_color       } if self.text_color        else {}
        b_color   = {'background_color':self.background_color } if self.background_color  else {}
        padding_x = {'padding_x'       :self.content_padding_x} if self.content_padding_x else {}
        padding_y = {'padding_y'       :self.content_padding_x} if self.content_padding_x else {}

        args = {}
        args.update( v_align   )
        args.update( h_align   )
        args.update( font_name )
        args.update( font_size )
        args.update( color     )
        args.update( b_color   )
        args.update( padding_x )
        args.update( padding_y )

        for column in self.columns :
            lbl = BindedLabel( 
                text=str( line[column] if column in line.keys() else '' ), \
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
            self._all_columns = sorted( self.headers.keys() )#sorted( data[0].keys() )

            #Filtering
            self._data = filter( self._validate_line, data )

            #Sorting
            if len( self.row_sorting ) > 0 :
                field, mode = self.row_sorting[0]
                reverse = False if mode == 'asc' else True
                self._data = sorted( self._data, key=lambda o: o[field], reverse=reverse )
         
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
        
        #{ 'name':lambda n: n.startswith('M') } 

        filters = {}
        filters_names = {}
        for column in self.grid._all_columns :
            chk, lbl, fil = self._columns[ column ]
            if len( fil.text.strip() ) > 0 :

                expression = fil.text.strip()
    
                if expression[0] in '< <= => > == != and or'.split(' ') :
                    foo = 'lambda VAL: %s' % ( 'VAL ' + expression )

                if '$VAL' in expression :                 
                    foo = 'lambda VAL: %s' % ( expression.replace('$VAL','VAL') )

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
        for column in self.grid._all_columns :
            chk, lbl, fil = self._columns[ column ]
            if chk.active :
                columns.append( column )
        return columns

    """
    Show customization panel.
    """
    def customize( self ) :
        self.popup = FlatPopup( 
            size_hint=(.7,.7), \
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

        footer = BoxLayout( orientation='horizontal', spacing=10, size_hint=(1,None), height=35 )        
        args = { 'size_hint':(.2,1), 'background_color':[0,.59,.53,1], 'background_color_down':[0,.41,.36,1] }
        
        txt = '[ref=main][b]       ?       [/b][/ref]'
        lbl = Label( text=txt, markup=True, color=[0,0,0,.8], font_size=18 )
        lbl.bind( on_ref_press=self._help_popup.open )

        cancel_button = FlatButton( text='X', **args )
        cancel_button.bind( on_press=self.exit_customizer )

        ok_button = FlatButton( text='OK', **args )
        ok_button.bind( on_press=self.save_and_exit )

        footer.add_widget( lbl )
        footer.add_widget( cancel_button )
        footer.add_widget( ok_button )
        return footer

    """
    Will build a single popup content row.
    """
    def _build_content_row( self, column ) :

        row = BoxLayout( orientation='horizontal', size_hint=(1,None), height=30 )
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
        x = BoxLayout( orientation='vertical', padding=[5,5,5,10] )
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
class ColumnHeader( BindedLabel ) :
    def __init__( self, **kargs ) :
        super( ColumnHeader, self ).__init__( **kargs )

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
        if touch.is_double_tap : return self.on_double_tap( touch )
        self._create_clock( touch )
        return True

    def on_touch_up( self, touch ) :
        self._delete_clock( touch )
        if self.grid : self.grid.on_row_select( self.rowid )
        return True

    def on_double_tap( self, touch ) :
        if self.grid : self.grid.on_row_double_tap( self.rowid )
        return True











