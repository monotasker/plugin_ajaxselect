from plugin_ajaxselect import AjaxSelect, get_linktable, FilteredOptionsWidget, FilteredMultipleOptionsWidget
from pprint import pprint
if 0:
    from gluon import current, SQLFORM, URL
    request, session, response = current.request, current.session, current.response
    db = current.db

def get_values():
    """
    Retrieve the current values from the widget's db table for refreshed widget.
    """
    tablename = request.args[0]
    fieldname = request.args[1]
    table = db[tablename]
    field = table[fieldname]
    multi = request.vars['multi'] if 'multi' in list(request.vars.keys()) else None
    orderby = request.vars['orderby'] if 'orderby' in list(request.vars.keys()) else None
    rval = request.vars['rval'] if 'rval' in list(request.vars.keys()) else None
    restricted = request.vars['restricted'] if 'restricted' in list(request.vars.keys()) else None
    restrictor = request.vars['restrictor'] if 'restrictor' in list(request.vars.keys()) else None
    sortable = request.vars['sortable'] if 'restricted' in list(request.vars.keys()) else None
    value = request.vars[fieldname]

    linktable = get_linktable(field)

    if not multi in [None, False, 'False']:
        if orderby or rval:
            w = FilteredMultipleOptionsWidget.widget(field, value,
                                             orderby=orderby,
                                             multiple='multiple',
                                             restricted=restricted,
                                             rval=rval)
        else:
            w = MultipleOptionsWidget.widget(field, value)
        #place selected items at end of sortable select widget
        if sortable:
            print('trying to sort values ===========================')
            print('value is', value)
            try:
                for v in value:
                    opt = w.element(_value=v)
                    i = w.elements().index(opt)
                    w.append(opt)
                    del w[i - 1]
            except AttributeError as e:
                if type(v) == 'IntType':
                    opt = w.element(_value=value)
                    i = w.elements().index(opt)
                    w.append(opt)
                    del w[i - 1]
                else:
                    print(e)
            except Exception as e:
                    print(e, type(e))
            pprint([e['_value'] for e in w.elements()])
    else:
        if orderby or rval:
            w = FilteredOptionsWidget.widget(field, value,
                                             orderby=orderby,
                                             restricted=restricted,
                                             rval=rval)
        else:
            w = OptionsWidget.widget(field, value)

    options = w.elements('option')
    return CAT(options)


def linked_edit_form():
    """
    creates a form to edit, update, or delete an intry in the linked table which
    populates the AjaxSelect widget.
    """
    try:
        tablename = request.args[0]
        fieldname = request.args[1]
        table = db[tablename]
        field = table[fieldname]

        linktable = get_linktable(field)

        this_row = request.args[2]
        wrappername = request.vars['wrappername']
        formname = '{}/edit'.format(tablename)

        form = SQLFORM(db[linktable], this_row)

        comp_url = URL('plugin_ajaxselect', 'set_widget.load',
                       args=[tablename, fieldname],
                       vars=request.vars)

        if form.process(formname=formname).accepted:
            response.flash = 'form accepted'
            response.js = "web2py_component('%s', '%s');" % (comp_url, wrappername)
        if form.errors:
            response.error = 'form was not processed'
            print('error processing linked_create_form')
            print(form.errors)
        else:
            pass
    except Exception:
        import traceback
        print('error in whole of linked_edit_form')
        print(traceback.format_exc(5))
        form = traceback.format_exc(5)

    return {'form': form}


def linked_create_form():
    """
    creates a form to insert a new entry into the linked table which populates
    the ajaxSelect widget
    """
    try:
        tablename = request.args[0]
        fieldname = request.args[1]
        wrappername = request.vars['wrappername']
        table = db[tablename]
        field = table[fieldname]

        linktable = get_linktable(field)

        formname = '{}_create'.format(wrappername)
        form = SQLFORM(db[linktable])

        comp_url = URL('plugin_ajaxselect', 'set_widget.load',
                    args=[tablename, fieldname],
                    vars=request.vars)

        if form.process(formname=formname).accepted:
            response.flash = 'form accepted'
            # response.js = "window.setTimeout(" \
            #               "web2py_component('{}', '{}'), " \
            #               "500);".format(comp_url, wrappername)

            # print 'linked create form accepted'
            # print 'linked create form vars:'
            # pprint(form.vars)
        if form.errors:
            response.error = 'form was not processed'
            response.flash = 'form was not processed'
            print('error processing linked_create_form')
            print(form.errors)
        else:
            # print 'form not processed but no errors'
            pass

    except Exception:
        import traceback
        print(traceback.format_exc(5))
        form = traceback.format_exc(5)

    return dict(form=form)
