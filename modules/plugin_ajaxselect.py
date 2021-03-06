from gluon import current, SPAN, A, UL, LI, OPTION, SELECT, LOAD, CAT
from gluon.html import URL
from gluon.sqlhtml import OptionsWidget, MultipleOptionsWidget
from .plugin_widgets import MODAL
from pprint import pprint
import traceback
# import copy
# TODO: add ListWidget as another option?

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
    interfere with one another when any one of them is refreshed.

    :param orderby (str; defaults to id): Takes the name of a field in the
    referenced table to be used for ordering the entries in the widget. By
    default the order is descending. If the field name is prefixed by ~ the
    order will be changed to descending.
    """
    # TODO: allow for restrictor argument to take list and filter multiple
    # other fields

    def __init__(self, field, value, indx=0,
                 refresher=None, adder=True,
                 restricted=None, restrictor=None,
                 multi=True, lister=False,
                 rval=None, sortable=False,
                 orderby=None):

        # raw args
        self.field = field
        self.indx = indx if indx else 0
        self.refresher = refresher
        self.adder = adder
        self.restrictor = restrictor
        self.restricted = restricted
        self.multi = multi
        self.lister = lister
        self.rval = rval
        self.sortable = sortable
        self.orderby = orderby

        # find table referenced by widget
        self.fieldset = str(field).split('.')
        self.linktable = get_linktable(field)
        # processed variables
        self.wrappername = '{}_{}'.format(self.fieldset[0], self.fieldset[1])
        self.form_name = '%s_adder_form' % self.linktable
        # for referenced table form

        # get the field value (choosing db or session here)
        self.value = value
        try:
            if value and len(value) > 0:
                self.clean_val = ','.join(map(str, value))
            else:
                self.clean_val = value
        except TypeError:
            self.clean_val = value
        # args for add and refresh urls
        self.uargs = self.fieldset
        # vars for add and refresh urls
        self.uvars = {'wrappername': self.wrappername,
                      'refresher': refresher,
                      'adder': self.adder,
                      'restrictor': self.restrictor,
                      'multi': self.multi,
                      'lister': self.lister,
                      'restricted': self.restricted,
                      'sortable': self.sortable,
                      'orderby': self.orderby,
                      'indx': self.indx}

    def widget(self):
        """
        Place initial load container for controller to fill.
        """
        wrapper = CAT()

        # create and add content of SPAN
        widget = self._create_widget()
        refreshlink = self._make_refresher(self.wrappername, self.linktable,
                                          self.uargs, self.uvars)
        adder, modal = self._make_adder(self.wrappername, self.linktable)
        wrapper.components.extend([widget, refreshlink, adder])

        # create and add tags/links if multiple select widget
        if self.multi and (self.lister == 'simple'):
            taglist = self._make_taglist()
        elif self.multi and (self.lister == 'editlinks'):
            taglist = self._make_linklist()
        else:
            taglist = ''
        wrapper.append(taglist)

        return wrapper, modal

    def _create_widget(self):
        """
        Create either a single select widget or multiselect widget
        """
        if self.multi not in [None, False, 'False']:
            if self.orderby or self.rval:
                w = FilteredMultipleOptionsWidget.widget(
                    self.field, self.value,
                    orderby=self.orderby,
                    multiple='multiple',
                    restricted=self.restricted,
                    rval=self.rval)
            else:
                w = MultipleOptionsWidget.widget(self.field, self.value)
            # place selected items at end of sortable select widget
            if self.sortable:
                print('trying to sort values =============')
                print('value is', self.value)
                try:
                    for v in self.value:
                        print('1')
                        opt = w.element(_value=str(v))
                        print('2')
                        i = w.elements().index(opt)
                        print('3')
                        w.append(opt)
                        print('4')
                        del w[i - 1]
                except AttributeError as e:
                    print('error with', v)
                    if type(v) == 'IntType':
                        opt = w.element(_value=self.value)
                        i = w.elements().index(opt)
                        w.append(opt)
                        del w[i - 1]
                    else:
                        print(e)
                except Exception as e:
                        print(e, type(e))
                pprint([elem['_value'] for elem in w.elements()])
        else:
            if self.orderby or self.rval or self.restrictor:
                w = FilteredOptionsWidget.widget(self.field, self.value,
                                                 orderby=self.orderby,
                                                 restricted=self.restricted,
                                                 rval=self.rval)
            else:
                w = OptionsWidget.widget(self.field, self.value)

        w['_id'] = '{}_{}'.format(self.fieldset[0], self.fieldset[1])
        w['_name'] = self.fieldset[1]
        myclasses = 'plugin_ajaxselect '
        if self.multi not in [None, False, 'False']:
            myclasses += 'multiple '
        if self.restrictor not in [None, 'None', 'none']:
            myclasses += 'restrictor for_{} '.format(self.restrictor)
        if self.restricted not in [None, 'None', 'none']:
            myclasses += 'restricted by_{} '.format(self.restricted)
        w['_class'] = myclasses

        return w

    def _make_refresher(self, wrappername, linktable, uargs, uvars):
        '''
        Return link to refresh this widget via ajax.

        The widget is always created, since its href attribute is used to pass
        several values to the client-side javascripts. If the widget is
        instantiated with the 'refresher' parameter set to False, then the
        link is hidden via CSS.
        '''
        refresher_id = '{}_refresh_trigger'.format(linktable)
        # prepare to hide 'refresh' button via CSS if necessary
        rstyle = ''
        if self.refresher in (False, 'False'):
            rstyle = 'display:none'
        comp_url = URL('plugin_ajaxselect', 'get_values',
                       args=self.uargs, vars=self.uvars)
        ajs = 'ajax("{url}", ["{n}"], "{wn}"); ' \
              'return false;'.format(url=comp_url,
                                     wn=self.wrappername,
                                     n=self.fieldset[1])
        refresh_link = A(SPAN(_class='glyphicon glyphicon-refresh'),
                         _onclick=ajs,
                         _href=comp_url, _id=refresher_id,
                         _class='refresh_trigger badge badge-info ',
                         _style=rstyle)

        return refresh_link

    def _make_adder(self, wrappername, linktable):
        '''Build link for adding a new entry to the linked table'''
        try:
            # attrs = {'_href': URL('plugin_ajaxselect',
            #                       'linked_create_form.load',
            #                       args=self.uargs, vars=self.uvars)}
            content = LOAD('plugin_ajaxselect', 'linked_create_form.load',
                           args=self.uargs, vars=self.uvars, ajax=True)
            adder = MODAL(SPAN(_class='glyphicon glyphicon-plus'),
                          'Add new {} item'.format(self.linktable),
                          content,
                          trigger_classes='add_trigger badge badge-success ',
                          trigger_type='link',
                          modal_classes='plugin_ajaxselect modal_adder',
                          # attributes=attrs,
                          id='{}_adder'.format(wrappername))
            add_trigger = adder[0]
            add_modal = adder[1]
            return add_trigger, add_modal
        except Exception:
            print(traceback.format_exc(5))

    def _make_taglist(self):
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
                    format_string = fmt(the_row) if callable(fmt) \
                        else fmt % the_row
                    listitem = LI(SPAN(format_string, _id=v,
                                       _class='label label-info'),
                                  _id=v, _class='tag')
                    listitem.append(A(
                        SPAN(_class='glyphicon glyphicon-remove'), _href='#',
                        _class='tag tag_remover label label-warning'))
                    taglist.append(listitem)
            else:
                pass
        except Exception:
            print(traceback.format_exc(5))
        return taglist

    def _make_linklist(self):
        """
        Build a list of selected widget options to be displayed as a
        list of 'tags' below the widget.
        """
        db = current.db
        xclasses = ' sortable' if self.sortable else ''
        ll = UL(_class='taglist editlist {}'.format(xclasses))

        # append the currently selected items to the list
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
                myargs.append(v)
                elink = MODAL(SPAN(_class='glyphicon glyphicon-edit'),
                              'Edit {} item {}'.format(self.linktable, v),
                              LOAD('plugin_ajaxselect',
                                   'linked_edit_form.load',
                                   args=myargs, vars=self.uvars, ajax=True),
                              trigger_classes='linklist_edit_trigger badge '
                              'badge-warning ',
                              trigger_type='link',
                              modal_classes='plugin_ajaxselect '
                              'modal_linklist_edit',
                              id='{}_{}'.format(self.linktable, v))
                ln.append(elink)
                ln.append(A(SPAN(_class='glyphicon glyphicon-remove'),
                            _class='tag tag_remover '
                                   'label label-important'))
                ll.append(ln)
        return ll

    # def get_classes(self, linktable, restricted, restrictor, lister,
    #                 sortable):
    #     """
    #     build classes for wrapper span to indicate filtering relationships
    #     """
    #     classlist = 'plugin_ajaxselect {} '.format(linktable)
    #     if not restrictor in [None, 'False']:
    #         classlist += 'restrictor restrictor_for_{} '.format(restrictor)
    #     if restricted and restricted != 'False':
    #         classlist += 'restricted restricted_by_{} '.format(restricted)
    #     if lister == 'simple':
    #         classlist += 'lister_simple '
    #     elif lister == 'editlinks':
    #         classlist += 'lister_editlinks '
    #     if sortable:
    #         classlist += 'sortable '
    #
    #     return classlist


class FilteredOptionsWidget(OptionsWidget):
    """
    Overrides the gluon.sqlhtml.OptionsWidget class to filter the list of
    options.
    The initial list of options comes via field.requires.options(). This
    furnishes a list of tuples, each of which contains the id and format
    string for one option from the referenced field.
    """

    @classmethod
    def widget(cls, field, value, restricted=None, restrictor=None, rval=None,
               orderby=None, multiple=False, **attributes):
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

        default = {'value': value}
        attributes.update({'_restricted': restricted,
                           '_orderby': orderby,
                           '_multiple': multiple})
        attr = cls._attributes(field, default, **attributes)

        # get raw list of options for this widget
        requires = field.requires
        if not isinstance(requires, (list, tuple)):
            requires = [requires]
        if requires:
            if hasattr(requires[0], 'options'):
                options = requires[0].options()
            else:
                raise SyntaxError(
                    'widget cannot get options of %s' % field)

        # get the table referenced by this field
        linktable = get_linktable(field)

        # get the value of the restricting field
        if restricted not in [None, 'None', 'none']:
            table = field.table
            filter_field = table[restricted]
            if rval:
                filter_val = rval
            else:
                if isinstance(value, list):
                    value = value[0]
                if isinstance(value, str):
                    value = value.replace("|", "")
                filter_row = db(field == value).select().first()
                filter_val = filter_row[filter_field] if filter_row else None
            if filter_val:
                # get the table referenced by the restricting field
                filter_linktable = get_linktable(filter_field)

                # find the linktable field that references filter_linktable
                reffields = db[linktable].fields
                ref = 'reference {}'.format(filter_linktable)
                cf = [f for f in reffields if db[linktable][f].type == ref][0]

                # filter and order raw list of options
                myorder = orderby if (orderby and orderby.replace('~', '')
                                      in reffields) else 'id'
                rows = db(db[linktable][cf] != None).select(orderby=myorder)
                rows = db(db[linktable][cf] == filter_val
                          ).select(orderby=myorder)
            else: rows = None
        else:
            reffields = db[linktable].fields
            myorder = orderby if (orderby and orderby.replace('~', '')
                                  in reffields) else 'id'
            rows = db(db[linktable].id > 0).select(orderby=myorder)

        # build widget with filtered and ordered options
        f_options = []
        value = value[0] if (isinstance(value, list) and
                             len([v for v in value if v]) == 1) else value
        if rows:
            if value:
                val_option = [o for r in rows for o in options
                              if o[0] and r.id == int(o[0])
                              and o[0] == str(value)]
                print('val_option', val_option)
                val_option = val_option[0]
                f_options.append(val_option)
            f_options.extend([o for r in rows for o in options
                              if o[0] and r.id == int(o[0])
                              and r.id != str(value)])
            opts = [OPTION(v, _value=k) for (k, v) in f_options]
        else:
            opts = []
        widget = SELECT(*opts, **attr)

        return widget


class FilteredMultipleOptionsWidget(MultipleOptionsWidget):
    """
    Overrides the gluon.sqlhtml. MultipleOptionsWidget class to filter the list
    of options.
    The initial list of options comes via field.requires.options(). This
    furnishes a list of tuples, each of which contains the id and format
    string for one option from the referenced field.
    """

    @classmethod
    def widget(cls, field, value, restricted=None, rval=None,
               orderby=None, multiple=True, **attributes):
        """
        generates a SELECT tag, including OPTIONs (only 1 option allowed)

        This method takes one argument more than MultipleOptionsWidget.widget.
        The restricted argument identifies the form field whose value
        constrains the values to be included as available options for this
        widget.

        see also:
            :meth:`FormWidget.widget`
            :meth:`OptionsWidget.widget`
            :meth:`MultipleOptionsWidget.widget`
        """
        db = current.db

        default = {'value': value}
        attributes.update({'_restricted': restricted,
                           '_orderby': orderby,
                           '_multiple': multiple})
        attr = cls._attributes(field, default, **attributes)

        # get raw list of options for this widget
        requires = field.requires
        if not isinstance(requires, (list, tuple)):
            requires = [requires]
        if requires:
            try:
                options = requires[0].options()
            except SyntaxError:
                print('widget cannot get options of %s' % field)

        # get the table referenced by this field
        linktable = get_linktable(field)

        # get the value of the restricting field
        if restricted not in [None, 'None', 'none']:
            table = field.table
            filter_field = table[restricted]
            if rval:
                filter_val = rval
            else:
                filter_row = db(field == value).select().first()
                filter_val = filter_row[filter_field]

            # get the table referenced by the restricting field
            filter_linktable = get_linktable(filter_field)

            # find the linktable field that references filter_linktable
            reffields = db[linktable].fields
            ref = 'reference {}'.format(filter_linktable)
            cf = [f for f in reffields if db[linktable][f].type == ref][0]

            # filter and order raw list of options
            myorder = orderby if (orderby and orderby.replace('~', '')
                                  in reffields) else 'id'
            rows = db(db[linktable][cf] == filter_val).select(orderby=myorder)
        else:
            reffields = db[linktable].fields
            myorder = orderby if (orderby and orderby.replace('~', '')
                                  in reffields) else 'id'
            rows = db(db[linktable].id > 0).select(orderby=myorder)

        # build widget with filtered and ordered options
        print(options)
        f_options = [o for r in rows for o in options
                     if o[0] and r.id == int(o[0])]
        opts = [OPTION(v, _value=k) for (k, v) in f_options]
        widget = SELECT(*opts, **attr)

        return widget


def get_linktable(field):
    """
    Return name of table for this widget from its 'requires' attribute.
    """
    requires = field.requires
    if not isinstance(field.requires, (list, tuple)):
        requires = [field.requires]

    try:
        linktable = requires[0].ktable
    except AttributeError:  # as when nested validators with IS_EMPTY_OR
        linktable = requires[0].other.ktable

    return linktable


def sanitize_int_list(val, delimiter='|'):
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
        val = val.split(delimiter)
        val = [sanitize_internal(v) for v in val]
        val = [v for v in val if v]
        val = val if len(val) else None
    else:
        val = sanitize_internal(val)
        val = [val] if val else None

    return val
