from gluon import current, SPAN, A, UL, LI, OPTION, SELECT, LOAD, CAT
from gluon.html import URL
from gluon.sqlhtml import OptionsWidget, MultipleOptionsWidget
from plugin_widgets import MODAL
import traceback
#import copy
#TODO: add ListWidget as another option?

"""
AjaxSelect process flow

AjaxSelect()
"""


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

    :param lister (False/'simple'/'editlinks'; defaults to False): 'simple'
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

    :param indx (int; defaults to 0): This value allows for multiple AjaxSelect
    widgets referencing the same table from a single form. Each field within
    the form's table should be given a different 'indx' value to differentiate
    the widget from others. Without this differentiating value the widgets will
    interfere with one another when any on of them is refreshed.
    """
    #TODO: allow for restrictor argument to take list and filter multiple
    #other fields

    def __init__(self, field, value, indx=0,
                 refresher=None, adder=True,
                 restricted=None, restrictor=None,
                 multi=True, lister=False,
                 rval=None, sortable=False):

        # raw args
        self.field = field
        self.indx = indx
        self.refresher = refresher
        self.adder = adder
        # isolate setting of param for easy overriding in subclasses
        self.restricted = self.restrict(restricted)
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

        # get the field value (choosing db or session here)
        self.value = self.choose_val(value)
        if value and len(value) > 0:
            self.clean_val = ','.join(map(str, value))
        else:
            self.clean_val = value
        # args for add and refresh urls
        self.uargs = self.fieldset
        print 'init: self.uargs is', self.uargs
        print 'init: value is', value
        # vars for add and refresh urls
        self.uvars = {'wrappername': self.wrappername,
                      'refresher': refresher,
                      'adder': self.adder,
                      'restrictor': self.restrictor,
                      'multi': self.multi,
                      'lister': self.lister,
                      'restricted': self.restricted,
                      'sortable': self.sortable}

    def widget(self):
        """
        Place initial load container for controller to fill.
        """
        # prepare classes for widget wrapper
        wclasses = self.get_classes(self.linktable, self.restricted,
                                    self.restrictor, self.lister, self.sortable)
        uvars = self.uvars
        uvars.update({self.fieldset[1]: self.value})
        # create SPAN to wrap widget
        wrapper = SPAN(_id=self.wrappername, _class=wclasses)
        wrapper.append(LOAD('plugin_ajaxselect', 'set_widget.load',
                            args=self.uargs, vars=uvars,
                            target=self.wrappername))
        print 'widget: uargs is', self.uargs
        return wrapper

    def widget_contents(self):
        """
        Main method to create the ajaxselect widget. Calls helper methods
        and returns the wrapper element containing all associated elements
        """
        #session = current.session
        #request = current.request

        wrapper = CAT()

        # create and add content of SPAN
        widget = self.create_widget()
        refreshlink = self.make_refresher(self.wrappername, self.linktable,
                                          self.uargs, self.uvars)
        adder = self.make_adder(self.wrappername, self.linktable)
        wrapper.components.extend([widget, refreshlink, adder])

        # create and add tags/links if multiple select widget
        if self.multi and (self.lister == 'simple'):
            taglist = self.make_taglist()
        elif self.multi and (self.lister == 'editlinks'):
            taglist = self.make_linklist()
        else:
            taglist = ''
        wrapper.append(taglist)

        return wrapper

    def get_widget_index(self):
        """
        Return an int differentiating widget from others referencing the same
        table.

        At present this simply returns the value of self.indx.
        """
        # TODO: Can this index be drawn automatically from the table
        # definition so that it doesn't have to be set manually?
        #db = current.db
        #table = db[self.field.table]
        #thefields = []
        #for f in [f for f in table.fields]:
            #if table[f].widget:
                #try:
                    #if table[f].requires.ktable == self.linktable:
                        #thefields.append(f)
                #except AttributeError:
                    #try:
                        #if table[f].requires[0].ktable == self.linktable:
                            #thefields.append(f)
                    #except IndexError:
                        #pass  # FIXME: problem with list:string fields
        #if len(thefields) > 1:  # FIXME: why are single fields picked up?
            #current_i = thefields.index(self.fieldset[1])
            #return current_i
        #else:
            #return None
        indx = self.indx if self.indx else 0
        return indx

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

    def sanitize_int_list(self, val):
        """
        Return val as a list of ints and not as plain int or str
        """
        def sanitize_internal(val):
            if not isinstance(val, int):
                try:
                    val = int(val)
                except (ValueError, TypeError):
                    val = None  # empty string or alphabetical
            return val

        if val and isinstance(val, list):
            val = [sanitize_internal(v) for v in val]
            val = [v for v in val if v]
        elif isinstance(val, str):
            val = val.split('|')
            val = [sanitize_internal(v) for v in val]
            val = [v for v in val if v]
            val = val if len(val) else None
        else:
            val = sanitize_internal(val)
            val = [val] if val else None

        return val

    def choose_val(self, value):
        """
        Use value stored in session if changes to widget haven't been sent to
        db session val must be reset to None each time it is checked.

        Always returns the value either as a list of integers or None.
        """
        session = current.session

        val = value
        if (self.wrappername in session.keys()):
            if session[self.wrappername]:
                val = session[self.wrappername]
                del session[self.wrappername]
            else:
                del session[self.wrappername]
        else:
            pass

        return self.sanitize_int_list(val)

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
                print 'val: ', self.value
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
        nm = self.wrappername.split('_')
        w['_id'] = '{}_{}'.format(nm[0], nm[1])
        w['_name'] = nm[1]
        return w

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
        comp_url = URL('plugin_ajaxselect', 'set_widget.load',
                       args=self.uargs, vars=self.uvars)
        nm = self.wrappername.split('_')
        ajs = 'ajax("{url}", ["{n}"], "{wn}"); ' \
              'return false;'.format(url=comp_url,
                                     wn=self.wrappername,
                                     n=nm[1])
                                     #n='{}_{}'.format(nm[0], nm[1]))
        refresh_link = A(u'\u200B', _onclick=ajs,
                         _href='#', _id=refresher_id,
                         _class='refresh_trigger badge badge-info icon-refresh',
                         _style=rstyle)

        return refresh_link

    def make_adder(self, wrappername, linktable):
        '''Build link for adding a new entry to the linked table'''
        #load = LOAD('plugin_ajaxselect', 'linked_create_form.load',
                    #args=self.uargs, vars=self.uvars, ajax=True)
        adder = MODAL(u'\u200B',
                      'Add new {} item'.format(self.linktable),
                      'None',
                      trigger_classes='add_trigger badge badge-success icon-plus',
                      trigger_type='link',
                      modal_classes='plugin_ajaxselect modal_adder')
        return adder

    def make_taglist(self):
        """Build a list of selected widget options to be displayed as a
        list of 'tags' below the widget."""
        try:
            db = current.db
            classes = 'taglist'
            if self.sortable:
                classes += ' sortable'
            taglist = UL(_class=classes)
            if self.value:
                for v in self.value:
                    the_row = db(db[self.linktable].id == v).select().first()
                    fmt = db[self.linktable]._format
                    format_string = fmt(the_row) if callable(fmt) else fmt % the_row
                    listitem = LI(SPAN(format_string, _id=v, _class='label label-info'),
                                _id=v, _class='tag')
                    listitem.append(A(u"\u200b", _href='#',
                                      _class='tag tag_remover icon-remove '
                                             'label label-important'))
                    taglist.append(listitem)
            else:
                pass
        except Exception:
            print traceback.format_exc(5)
        return taglist

    def make_linklist(self):
        """
        Build a list of selected widget options to be displayed as a
        list of 'tags' below the widget.
        """
        db = current.db
        xclasses = ' sortable' if self.sortable else ''
        ll = UL(_class='taglist editlist {}'.format(xclasses))

        #append the currently selected items to the list
        if self.value:
            for v in listcheck(self.value):
                myrow = db(db[self.linktable].id == v).select().first()
                if myrow is None:
                    continue
                try:
                    fmt = db[self.linktable]._format
                    formatted = fmt(myrow) if callable(fmt) else fmt % myrow
                except TypeError:
                    formatted = myrow[1]
                linkargs = self.uargs[:]  # new obj so vals don't pile up
                linkargs.append(v)
                ln = LI(SPAN(formatted, _class='badge badge-info'),
                        _id=v, _class='editlink tag')
                myargs = self.uargs[:]
                print 'making linklist: self.uargs is', self.uargs
                myargs.append(v)
                print 'making linklist: myargs is ', myargs
                elink = MODAL(u'\u200B',
                              'Edit {} item {}'.format(self.linktable, v),
                              LOAD('plugin_ajaxselect', 'linked_edit_form.load',
                                  args=myargs, vars=self.uvars, ajax=True),
                              trigger_classes='linklist_edit_trigger badge badge-warning icon-edit',
                              trigger_type='link',
                              modal_classes='plugin_ajaxselect modal_linklist_edit',
                              id='{}_{}'.format(self.linktable, v))
                ln.append(elink)
                ln.append(A(u'\u200B',
                            _class='tag tag_remover icon-remove '
                                   'label label-important'))
                ll.append(ln)
        return ll

    def get_classes(self, linktable, restricted, restrictor, lister, sortable):
        """
        build classes for wrapper span to indicate filtering relationships
        """
        classlist = 'plugin_ajaxselect {} '.format(linktable)
        if not restrictor in [None, 'False']:
            classlist += 'restrictor_for_{} '.format(restrictor)
        if restricted and restricted != 'False':
            classlist += 'restricted_by_{} '.format(restricted)
        if lister == 'simple':
            classlist += 'lister_simple '
        elif lister == 'editlinks':
            classlist += 'lister_editlinks '
        if sortable:
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

        # get the value of the restricting field
        table = field.table
        filter_field = table[restricted]
        if rval:
            filter_val = rval
        else:
            filter_row = db(field == value).select().first()
            filter_val = filter_row[filter_field]

        # get the table referenced by the restricting field
        filter_req = filter_field.requires
        if not isinstance(filter_req, (list, tuple)):
            filter_req = [filter_req]
        filter_linktable = filter_req[0].ktable

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
