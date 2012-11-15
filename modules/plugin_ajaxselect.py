from gluon import current, SPAN, A, INPUT, UL, LI, OPTION, SELECT
from gluon.html import URL
from gluon.sqlhtml import OptionsWidget, MultipleOptionsWidget
#TODO: add ListWidget as another option?


class AjaxSelect(object):
    """
    This plugin creates a select widget wrapped that can be refreshed via ajax
    without resetting the entire form. It also provides an "add new" button
    that allows users to add a new item to the table that populates the select
    widget via ajax. The widget is then automatically refreshed via ajax so
    that the new item is visible as a select option and can be chosen. All of
    this happens without a page or form refresh so that data entered in other
    fields is not lost or submitted.

    Installation:
    1. download the plugin file;
    2. In the web2py online ide (design view for your app) scroll to the bottom
    section labeled "Plugins";
    3. At the bottom of that section is a widget to "upload plugin file". Click
    "Browse".
    4. In the file selection window that opens, navigate to the downloaded
    plugin file, select it, and click "open". The file selection window should
    close.
    5. Click the "upload" button.
    6. Add the following three lines to the top of a module file to make db
    available in the 'current' object and to include the js and css files for
    the plugin:

    from gluon import current
    current.db = db
    response.files.append(URL('static',
                          'plugin_ajaxselect/plugin_ajaxselect.css'))
    response.files.append(URL('static',
                          'plugin_ajaxselect/plugin_ajaxselect.js'))

    The plugin should now be installed and ready to use.

    Usage:
    In a web2py model file, import this class and then apply it as
    the widget-factory for one or more db fields. To do this for a field named
    'author' from a table named 'notes' you would add this line somewhere in
    the model file:

    db.notes.author.widget = lambda field, value: AjaxSelect(field, value,
    {optional arguments}).widget()

    Optional arguments:
    :param refresher (True/False; defaults to True):a button to manually
    refresh the select widget via ajax.

    :param adder (True/False; defaults to True): a button to add a new record
    to the linked table that populates the select widget.

    :param restrictor ({form field name}): adds a dynamic constraint on the
    records displayed in the named field's widget. When the specified form
    field (within the same form) has its value changed, this select will be
    refreshed and its displayed records filtered accordingly. Note that this
    is only useful if {fieldname} references values shared with the linked
    table.

    e.g., to make the select constrain the widget for the 'works' table:
    db.notes.author.widget = lambda field, value: AjaxSelect(field, value,
    'authors', restrictor='work').widget()

    :param multi ('basic'/False; defaults to False): Instead of displaying a
    single select widget, the 'basic' value displays a standard multiselect
    widget (an html select widget with a size greater than 1). This will only
    work properly if the database field type is defined as "list:reference" in
    the model.

    :param lister (False/'simple'/'editlinks'; defaults to False): 'normal'
    adds a list of the widget's currently selected values below a multiselect
    widget. If set to 'editlinks' these passive list items become links opening
    edit forms for the linked items in a modal window.

    :param sortable (True/False; defaults to False): 'True' allows for
    drag-and-drop sorting of widget values (using jQuery-ui sortable). The
    sorted order is preserved in the database value for the field. In this
    mode the tags are also displayed in a single column rather than wrapping.

    Note that in order to use the 'sortable' parameter on a list that is
    created after page load (i.e., in a component), you will also need to add
    this short script to the bottom of the component view in which the list is
    created:

    <script>
    $('#my-sortable-id').sortable();
    $('#my-sortable-id').disableSelection();
    </script>

    This should instantiate the sortable object after the list has been
    created. If you wish to set any parameters on the sortable it should be
    done in this script.
    """
    #TODO: allow for restrictor argument to take list and filter multiple
    #other fields

    def __init__(self):
        verbose = 0
        if verbose == 1:
            print '------------------------------------------------'
            print 'starting modules/plugin_ajaxselect __init__'

    def widget(self, field, value, restricted=None, refresher=False,
                adder=True, restrictor=None, multi=False, lister=False,
                rval=None, sortable=False):
        """
        Main method to create the ajaxselect widget. Calls helper methods
        and returns the wrapper element containing all associated elements
        """
        session, request = current.session, current.request

        verbose = 0
        if verbose == 1:
            print '-------------------------------------------------'
            print 'starting AjaxSelect.widget() for ,', field

        if multi == 'False':
            multi = False
        elif multi == 'True':
            multi = True
        if verbose == 1:
            print multi, type(multi)
        #assemble information first
        fieldset = str(field).split('.')
        wrappername = self.wrappername(fieldset)
        linktable = self.linktable(field)  # find table referenced by widget
        form_name = '%s_adder_form' % linktable  # for referenced table form
        value = self.choose_val(value, wrappername)  # choose db or session
        clean_val = self.clean(value, multi)
        uargs = fieldset  # args for add and refresh urls
        restricted = self.restricted(restricted)  # isolate setting of param
        uvars = dict(linktable=linktable,
                    wrappername=wrappername, refresher=refresher,
                    adder=adder, restrictor=restrictor,
                    multi=multi, lister=lister,
                    restricted=restricted,
                    sortable=sortable,
                    value=clean_val)  # vars for add and refresh urls

        # create and assemble elements of widget
        wrapper = SPAN(_id=wrappername,
                    _class=self.classes(linktable, restricted,
                                        restrictor, lister, sortable))
        wrapper.append(self.create_widget(field, value, clean_val,
                                        multi, restricted, rval, sortable))
        wrapper.append(self.hidden_ajax_field(wrappername, clean_val))
        wrapper.append(self.refresher(wrappername, linktable, uargs, uvars))
        wrapper.append(self.adder(wrappername, linktable,
                                uargs, uvars, form_name))
        if multi and lister == 'simple':
            wrapper.append(self.taglist(value, linktable, sortable))
        elif multi and lister == 'editlinks':
            wrapper.append(self.linklist(value, linktable, uargs, uvars,
                sortable))
        else:
            if verbose == 1:
                print 'did not request list of tags'

        return wrapper

    def wrappername(self, fieldset):
        """
        Assemble id for the widget wrapper element
        >>>wrappername([foo, bar])
        'foo_bar_loader'
        """
        return '%s_%s_loader' % (fieldset[0], fieldset[1])

    def linktable(self, field):
        """
        Get name of table referenced by this widget from the widget's
        requires attribute.
        """

        if not isinstance(field.requires, list):
            requires = [field.requires]
        else:
            requires = field.requires
        linktable = requires[0].ktable

        return linktable

    def choose_val(self, val, wrappername):
        """
        Use value stored in session if changes to widget haven't been sent to
        db session val must be reset to None each time it is checked.
        """
        debug = False
        if debug: print '---------------'
        if debug: print 'starting modules/plugin_ajaxselect choose_val'

        session = current.session

        if (wrappername in session) and (session[wrappername]):
            val = session[wrappername]
            if debug: print 'session value being used in module: %s' % val
            session[wrappername] = None
        else:
            if debug: print 'db value being used in module: %s' % val
            session[wrappername] = None
        #make sure strings are converted to int and lenth-1 lists to single val
        if type(val) == list:
            try:
                if (val == []) or (val[0] == '' and len(val) < 2):
                    val = None
                elif val and len(val) < 2:
                    val = val[0]
                else:
                    val = [int(v) for v in val]
            except ValueError, e:
                print e
                val = None  # to handle a blank string being passed to int(v)
            except IndexError, e:
                print e
                val = None  # to handle an empty list

        if debug: print 'val at end of choose_val() =', val

        return val

    def clean(self, value, multi):
        verbose = 0
        clean = value
        #remove problematic pipe characters or commas from the field value
        #in case of list:reference fields
        if multi and multi != 'False' and isinstance(value, list):
            clean = ','.join(map(str, value))
        if verbose == 1:
            print 'value = ', value, type(value)
            print 'clean = ', clean, type(clean)

        return clean

    def restricted(self, restricted):
        """Isolate creation of this value so that it can be overridden in
        child classes."""

        return None

    def create_widget(self, field, value, clean_val, multi, restricted, rval,
            sortable):
        """
        create either a single select widget or multiselect widget
        """
        debug = False
        if debug:
            print 'starting create_widget()'
            print 'field =', field
            print 'value =', value

        if multi and multi != 'False':
            w = MultipleOptionsWidget.widget(field, value)
            if debug:
                print 'multiple options'

            #place selected items at end of sortable select widget
            if sortable:
                try:
                    for v in value:
                        if debug: print 'v =', v
                        opt = w.element(_value=v)
                        if debug: print 'opt =', opt
                        i = w.elements().index(opt)
                        w.append(opt)
                        del w[i - 1]
                        if debug:
                            print 'removed', opt
                            print 'index', i
                except AttributeError, e:
                    if type(v) == 'IntType':
                        opt = w.element(_value=value)
                        i = w.elements().index(opt)
                        w.append(opt)
                        del w[i - 1]
                    else:
                        print e
                except ValueError, e:
                        print e
                        print 'could not move', opt
                except TypeError, e:
                        print e

        else:
            w = OptionsWidget.widget(field, value)

        return w

    def hidden_ajax_field(self, wrappername, clean_val):
        """hidden input to help send unsaved changes via ajax so that they're
        preserved through a widget refresh"""

        inputid = wrappername + '_input'
        i = INPUT(_id=inputid, _name=inputid, _type='hidden',
                _value=clean_val)

        return i

    def refresher(self, wrappername, linktable, uargs, uvars):
        '''create link to refresh this widget via ajax. The widget is always
        created, since its href attribute is used to pass several values
        to the client-side javascripts. If the widget is instantiated with
        the 'refresher' parameter set to False, then the link is hidden
        via CSS.'''

        refresher_id = '%s_refresh_trigger' % linktable
        #prepare to hide 'refresh' button via CSS if necessary
        rstyle = ''
        if self.refresher in (False, 'False'):
            rstyle = 'display:none'
        #URL to refresh widget via ajax
        comp_url = URL('plugin_ajaxselect', 'set_widget.load',
                            args=uargs, vars=uvars)
        #create 'refresh' button
        refresh_a = A('r', _href=comp_url, _id=refresher_id,
                        _class='refresh_trigger', cid=wrappername,
                        _style=rstyle)

        return refresh_a

    def adder(self, wrappername, linktable, uargs, uvars, form_name):
        '''Build link for adding a new entry to the linked table'''

        #create id for adder link
        add_id = '{}_add_trigger'.format(linktable)
        #URL to load form for linking table via ajax
        add_url = URL('plugin_ajaxselect', 'set_form_wrapper.load',
                           args=uargs, vars=uvars)
        #create 'add new' button to open form
        add_a = A('+', _href=add_url, _id=add_id,
                    _class='add_trigger', cid=form_name)

        return add_a

    def taglist(self, value, linktable, sortable):
        """Build a list of selected widget options to be displayed as a
        list of 'tags' below the widget."""
        verbose = 0

        if verbose == 1:
            print '----------------------------------------------'
            print 'starting models/plugin_ajaxselect add_tags'
            print self.value

        db = current.db

        classes = 'taglist'
        if sortable:
            classes += ' sortable'
        tl = UL(_class=classes)
        if type(value) != list:
            value = [value]
        for v in value:
            the_row = db(db[linktable].id == v).select().first()
            f = db[linktable]._format % the_row
            ln = LI(f, _id=v, _class='tag')
            ln.insert(0, A('X', _class='tag_remover'))
            tl.append(ln)

        return tl

    def linklist(self, value, linktable, uargs, uvars, sortable):
        """Build a list of selected widget options to be displayed as a
        list of 'tags' below the widget."""

        debug = False
        if debug:
            print '----------------------------------------------'
            print 'starting models/plugin_ajaxselect add_tags'
            print value

        db = current.db
        form_name = '%s_editlist_form' % linktable

        #create list to hold linked tags
        ul_classes = 'taglist editlist'
        if sortable:
            ul_classes += ' sortable'
        ll = UL(_class=ul_classes)

        #append the currently selected items to the list
        if value:
            if type(value) != list:
                value = [value]

            for v in value:
                myrow = db(db[linktable].id == v).select().first()
                if myrow is None:
                    continue
                try:
                    formatted = db[linktable]._format % myrow
                except TypeError:
                    formatted = myrow[1]
                trigger_id = '%s_editlist_trigger_%i' % (linktable, int(v))
                linkargs = uargs[:]  # slice for new obj so vals don't pile up
                linkargs.append(v)
                ln = LI(SPAN(formatted), _id=v, _class='editlink tag')
                ln.insert(0, A('X', _class='tag_remover'))
                ln.insert(1, A('edit',
                                _href=URL('plugin_ajaxselect',
                                            'set_form_wrapper.load',
                                            args=linkargs,
                                            vars=uvars),
                                _id=trigger_id,
                                _class='edit_trigger editlink tag',
                                cid=form_name))
                ll.append(ln)
        return ll

    def classes(self, linktable, restricted, restrictor, lister, sortable):
        """
        build classes for wrapper span to indicate filtering relationships
        """

        c = 'plugin_ajaxselect '
        if restrictor and restrictor != 'False':
            c += '{} restrictor for_{} '.format(linktable, restrictor)
        if restricted and restricted != 'False':
            c += '{} restricted by_{}'.format(linktable, restricted)
        if lister == 'simple':
            c += 'lister_simple '
        elif lister == 'editlinks':
            c += 'lister_editlinks '
        if sortable:
            c += 'sortable '

        return c


class FilteredAjaxSelect(AjaxSelect):
    """
    This class extends the AjaxSelect base class to provide a select
    widget whose options are filtered in real time (via ajax refresh) based
    on the value set in another AjaxSelect widget in the same form.
    """

    def restricted(self, restricted):
        """Override parent restricted() method to allow a defined parameter
        with this name to take effect."""

        return restricted

    def create_widget(self, field, value, clean_val, multi, restricted, rval):
        """create either a single select widget or multiselect widget"""

        print '----------------------------------------------'
        print 'starting FilteredAjaxSelect.create_widget()'
        if multi:
            w = MultipleOptionsWidget.widget(field, value)
            #TODO: Create filtered multiple options widget class
        else:
            if rval:
                w = FilteredOptionsWidget.widget(field, value,
                                                 restricted, rval)
            else:
                w = OptionsWidget.widget(field, value)

        return w


class FilteredOptionsWidget(OptionsWidget):
    """
    Overrides the gluon.sqlhtml.OptionsWidget class to filter the list of
    options.
    The initial list of options comes via field.requires.options(). This
    furnishes a list of tuples, each of which contains the id and format
    string for one option from the referenced field.
    """

    @classmethod
    def widget(cls, field, value, restricted, rval, **attributes):
        """
        generates a SELECT tag, including OPTIONs (only 1 option allowed)

        This method takes one argument more than OptionsWidget.widget. The
        restricted argument identifies the form field whose value constrains
        the values to be included as available options for this widget.

        see also:
            :meth:`FormWidget.widget`
            :meth:`OptionsWidget.widget`
        """
        db = current.db

        default = dict(value=value)
        attr = cls._attributes(field, default, **attributes)

        print '----------------------------------------'
        print 'starting FilteredOptionsWidget.widget()'
        # get raw list of options for this widget
        requires = field.requires
        if not isinstance(requires, (list, tuple)):
            requires = [requires]
        if requires:
            if hasattr(requires[0], 'options'):
                options = requires[0].options()
            else:
                raise SyntaxError, 'widget cannot get options of %s' % field

        # get the table referenced by this field
        linktable = requires[0].ktable
        print 'getting options for table ', linktable

        # get the value of the restricting field
        table = field.table
        filter_field = table[restricted]
        if rval:
            filter_val = rval
            print 'new restricting value is ', rval
        else:
            filter_row = db(field == value).select().first()
            print 'restricting row is ', filter_row
            filter_val = filter_row[filter_field]
            print 'new restricting value is ', filter_val
        print 'filter_field', filter_field
        print 'filter_val', filter_val

        # get the table referenced by the restricting field
        filter_req = filter_field.requires
        if not isinstance(filter_req, (list, tuple)):
            filter_req = [filter_req]
        filter_linktable = filter_req[0].ktable
        print 'filter_linktable', filter_linktable

        #find the linktable field that references filter_linktable
        ref = 'reference %s' % filter_linktable
        cf = [f for f in db[linktable].fields
                                        if db[linktable][f].type == ref][0]

        # filter raw list of options
        f_options = [o for o in options if db((db[linktable].id == o[0])
                                & (db[linktable][cf] == filter_val)).select()]

        # build widget with filtered options
        opts = [OPTION(v, _value=k) for (k, v) in f_options]

        return SELECT(*opts, **attr)
