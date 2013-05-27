from gluon import current, SPAN, A, INPUT, UL, LI, OPTION, SELECT
from gluon.html import URL
from gluon.sqlhtml import OptionsWidget, MultipleOptionsWidget
import copy
#TODO: add ListWidget as another option?


def listcheck(val):
    """
    Returns the value as a list, whether or not it was a list to begin with.

    This is useful for avoiding index errors in situations where a value might
    be a length-1 list or might be an int or string.
    """
    if isinstance(val, list):
        return val
    else:
        return [val]


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

    def __init__(self, field, value, linktable,
                 refresher=None, adder=True,
                 restricted=None, restrictor=None,
                 multi=False, lister=False,
                 rval=None, sortable=False):
        self.verbose = 1
        if self.verbose == 1:
            print '------------------------------------------------'
            print 'starting modules/plugin_ajaxselect __init__'
        # raw args
        self.field = field
        self.refresher = refresher
        self.adder = adder
        self.restricted = self.restrict(restricted)  # isolate setting of param
        self.restrictor = restrictor
        self.multi = multi
        self.lister = lister
        self.rval = rval
        self.sortable = sortable

        # find table referenced by widget
        self.fieldset = str(field).split('.')
        self.linktable = self.get_linktable(field)

        # processed variables
        self.wrappername = self.get_wrappername(self.fieldset)
        self.form_name = '%s_adder_form' % self.linktable  # for referenced table form

        if self.verbose == 1:
            print multi, type(multi)

        # get the field value (choosing db or session here)
        self.value = self.choose_val(value)
        self.clean_val = self.sanitize_valstring(value)
        # args for add and refresh urls
        self.uargs = self.fieldset
        # vars for add and refresh urls
        self.uvars = {'linktable': self.linktable,
                      'wrappername': self.wrappername,
                      'refresher': refresher,
                      'adder': self.adder,
                      'restrictor': self.restrictor,
                      'multi': self.multi,
                      'lister': self.lister,
                      'restricted': self.restricted,
                      'sortable': self.sortable,
                      'value': self.clean_val}

    def widget(self):
        """
        Main method to create the ajaxselect widget. Calls helper methods
        and returns the wrapper element containing all associated elements
        """
        session, request = current.session, current.request
        if self.verbose == 1:
            print '-------------------------------------------------'
            print 'starting AjaxSelect.widget() for ,', self.field

        # prepare classes for widget wrapper
        w_classes = self.get_classes(self.linktable, self.restricted,
                                 self.restrictor, self.lister, self.sortable)
        # create SPAN to wrap widget
        wrapper = SPAN(_id=self.wrappername, _class=w_classes)

        # create and add content of SPAN
        widget = self.create_widget()
        hiddenfield = self.hidden_ajax_field()
        refreshlink = self.make_refresher(self.wrappername, self.linktable,
                                   self.uargs, self.uvars)
        adder = self.make_adder(self.wrappername, self.linktable)
        wrapper.components.extend([widget, hiddenfield, refreshlink, adder])

        # create and add tags/links if multiple select widget
        if self.multi and (self.lister == 'simple'):
            taglist = self.make_taglist(self.value, self.linktable, self.sortable)
        elif self.multi and (self.lister == 'editlinks'):
            taglist = self.make_linklist(self.value, self.linktable, self.uargs,
                                    self.uvars, self.sortable)
        else:
            taglist = ''
        wrapper.append(taglist)

        return wrapper

    def get_widget_index(self):
        """
        Return for other widgets pointing to same linktable
        """
        db = current.db
        table = db[self.field.table]
        thefields = []
        for f in [f for f in table.fields]:
            if table[f].widget:
                try:
                    if table[f].requires.ktable == self.linktable:
                        thefields.append(f)
                except AttributeError:
                    try:
                        if table[f].requires[0].ktable == self.linktable:
                            thefields.append(f)
                    except IndexError:
                        pass  # FIXME: problem with list:string fields
        if len(thefields) > 1:  # FIXME: why are single fields picked up?
            current_i = thefields.index(self.fieldset[1])
            return current_i
        else:
            return None

    def get_wrappername(self, fieldset):
        """
        Return id string for the widget wrapper element.

        Make sure that widgets using the same link table have distinct ids,
        using get_widget_index() method.
        """
        windex = self.get_widget_index()
        if not windex:
            windex = 0
        name = '{}_{}_loader{}'.format(fieldset[0], fieldset[1], str(windex))
        return name

    def get_linktable(self, field):
        """
        Return name of table for this widget from its 'requires' attribute.
        """
        if not isinstance(field.requires, list):
            requires = [field.requires]
        else:
            requires = field.requires
        linktable = requires[0].ktable

        return linktable

    def sanitize_int(self, val):
        """
        Return val as an int and not as a single-item list.
        """
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
        return val

    def choose_val(self, value):
        """
        Use value stored in session if changes to widget haven't been sent to
        db session val must be reset to None each time it is checked.
        """
        session = current.session
        if (self.wrappername in session) and (session[self.wrappername]):
            val = copy(session[self.wrappername])
            session[self.wrappername] = None
        else:
            val = value
            session[self.wrappername] = None

        return self.sanitize_int(val)

    def sanitize_valstring(self, value):
        """
        Return list:reference value string without problematic characters.
        """
        if (not self.multi in [None, 'False']) and isinstance(value, list):
            return ','.join(map(str, value))
        elif value:
            return value
        else:
            return None

    def restrict(self, restricted):
        """Isolate creation of this value so that it can be overridden in
        child classes."""
        return None

    def create_widget(self):
        """
        create either a single select widget or multiselect widget
        """
        if not self.multi in [None, 'False']:
            w = MultipleOptionsWidget.widget(self.field, self.value)

            #place selected items at end of sortable select widget
            if self.sortable:
                try:
                    for v in self.value:
                        opt = w.element(_value=v)
                        i = w.elements().index(opt)
                        w.append(opt)
                        del w[i - 1]
                except AttributeError, e:
                    if type(v) == 'IntType':
                        opt = w.element(_value=self.value)
                        i = w.elements().index(opt)
                        w.append(opt)
                        del w[i - 1]
                    else:
                        print e
                except Exception, e:
                        print e, type(e)
        else:
            w = OptionsWidget.widget(self.field, self.value)

        return w

    def hidden_ajax_field(self):
        """
        Return hidden input to help send unsaved changes via ajax so that
        they're preserved through a widget refresh
        """
        # TODO: this is unnecessary - fix ajax function
        inputid = self.wrappername + '_input'
        i = INPUT(_id=inputid, _name=inputid, _type='hidden',
                _value=self.clean_val)
        return i

    def make_refresher(self, wrappername, linktable, uargs, uvars):
        '''
        Return link to refresh this widget via ajax.

        The widget is always created, since its href attribute is used to pass
        several values to the client-side javascripts. If the widget is
        instantiated with the 'refresher' parameter set to False, then the
        link is hidden via CSS.
        '''
        refresher_id = '%s_refresh_trigger' % linktable
        #prepare to hide 'refresh' button via CSS if necessary
        rstyle = ''
        if self.refresher in (False, 'False'):
            rstyle = 'display:none'
        #URL to refresh widget via ajax
        comp_url = URL('plugin_ajaxselect', 'set_widget.load',
                       args=self.uargs, vars=self.uvars)
        #create 'refresh' button
        refresh_link = A('r', _href=comp_url, _id=refresher_id,
                         _class='refresh_trigger',
                         cid=self.wrappername,
                         _style=rstyle)

        return refresh_link

    def make_adder(self, wrappername, linktable):
        '''Build link for adding a new entry to the linked table'''

        #create id for adder link
        add_id = '{}_add_trigger'.format(self.linktable)
        #URL to load form for linking table via ajax
        add_url = URL('plugin_ajaxselect', 'set_form_wrapper.load',
                      args=self.uargs, vars=self.uvars)
        #create 'add new' button to open form
        add_link = A('+', _href=add_url, _id=add_id,
                     _class='add_trigger', cid=self.form_name)

        return add_link

    def make_taglist(self):
        """Build a list of selected widget options to be displayed as a
        list of 'tags' below the widget."""
        db = current.db
        classes = 'taglist'
        if self.sortable:
            classes += ' sortable'
        taglist = UL(_class=classes)
        for v in listcheck(self.value):
            the_row = db(db[self.linktable].id == v).select().first()
            format_string = db[self.linktable]._format % the_row
            listitem = LI(format_string, _id=v, _class='tag')
            listitem.insert(0, A('x', _class='tag_remover'))
            taglist.append(listitem)
        return taglist

    def make_linklist(self, value, linktable, uargs, uvars, sortable):
        """
        Build a list of selected widget options to be displayed as a
        list of 'tags' below the widget.
        """
        db = current.db
        form_name = '{}_editlist_form'.format(self.linktable)
        #create list to hold linked tags
        ul_classes = 'taglist editlist'
        if sortable:
            ul_classes += ' sortable'
        ll = UL(_class=ul_classes)

        #append the currently selected items to the list
        if self.value:
            for v in listcheck(self.value):
                myrow = db(db[self.linktable].id == v).select().first()
                if myrow is None:
                    continue
                try:
                    formatted = db[self.linktable]._format % myrow
                except TypeError:
                    formatted = myrow[1]
                trigger_id = '%s_editlist_trigger_%i' % (self.linktable, int(v))
                linkargs = self.uargs[:]  # new obj so vals don't pile up
                linkargs.append(v)
                ln = LI(SPAN(formatted), _id=v, _class='editlink tag')
                ln.insert(0, A('X', _class='tag_remover'))
                ln.insert(1, A('edit',
                               _href=URL('plugin_ajaxselect',
                                         'set_form_wrapper.load',
                                         args=linkargs,
                                         vars=self.uvars),
                               _id=trigger_id,
                               _class='edit_trigger editlink tag',
                               cid=form_name))
                ll.append(ln)
        return ll

    def get_classes(self, linktable, restricted, restrictor, lister, sortable):
        """
        build classes for wrapper span to indicate filtering relationships
        """
        classlist = 'plugin_ajaxselect '
        if not self.restrictor in [None, 'False']:
            classlist += '{} restrictor for_{} '.format(self.linktable,
                                                     self.restrictor)
        if self.restricted and restricted != 'False':
            classlist += '{} restricted by_{}'.format(self.linktable,
                                                   self.restricted)
        if self.lister == 'simple':
            classlist += 'lister_simple '
        elif self.lister == 'editlinks':
            classlist += 'lister_editlinks '
        if self.sortable:
            classlist += 'sortable '

        return classlist


class FilteredAjaxSelect(AjaxSelect):
    """
    This class extends the AjaxSelect base class to provide a select
    widget whose options are filtered in real time (via ajax refresh) based
    on the value set in another AjaxSelect widget in the same form.
    """

    def restrict(self, restricted):
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
    Overrides the gluon.sqlhtml. OptionsWidget class to filter the list of
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
            try:
                options = requires[0].options()
            except SyntaxError:
                print 'widget cannot get options of %s' % field

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
