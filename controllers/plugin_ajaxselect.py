from plugin_ajaxselect import AjaxSelect, FilteredAjaxSelect
if 0:
    from gluon import current, SQLFORM, URL
    request, session, response = current.request, current.session, current.response
    db = current.db


def set_widget():
    """
    Return a replacement AjaxSelect or FilteredAjaxSelect widget via ajax.
    """
    #get variables to build widget for the proper field

    tablename = request.args[0]
    fieldname = request.args[1]
    table = db[tablename]
    field = table[fieldname]
    requires = field.requires
    if not isinstance(requires, list):
        requires = [requires]
    linktable = requires[0].ktable

    value = request.vars[fieldname]
    rval = request.vars['rval'] if 'rval' in request.vars.keys() else None
    kwargs = {'indx': request.vars['indx'],
              'refresher': request.vars['refresher'],
              'adder': request.vars['adder'],
              'restrictor': request.vars['restrictor'],
              'multi': request.vars['multi'],
              'lister': request.vars['lister'],
              'restricted': request.vars['restricted'],
              'sortable': request.vars['sortable'],
              'orderby': request.vars['orderby']}
    #print 'controller: kwargs is ', kwargs
    if request.vars['restricted'] in (None, 'None'):
        w = AjaxSelect(field, value, **kwargs).widget_contents()
    else:
        w = FilteredAjaxSelect(field, value, rval=rval, **kwargs).widget_contents()

    return dict(wrapper=w,
                linktable=linktable,
                tablename=tablename,
                wrappername=request.vars['wrappername'])


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

        req = field.requires if isinstance(field.requires, list) else [field.requires]
        linktable = req[0].ktable

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
            print 'error processing linked_create_form'
            print form.errors
        else:
            pass
    except Exception:
        import traceback
        print 'error in whole of linked_edit_form'
        print traceback.format_exc(5)
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

        req = field.requires if isinstance(field.requires, list) \
            else [field.requires]
        linktable = req[0].ktable

        formname = '{}/create'.format(tablename)
        form = SQLFORM(db[linktable])

        comp_url = URL('plugin_ajaxselect', 'set_widget.load',
                    args=[tablename, fieldname],
                    vars=request.vars)

        if form.process(formname=formname).accepted:
            response.flash = 'form accepted'
            response.js = "web2py_component('%s', '%s');" % (comp_url, wrappername)
        if form.errors:
            response.error = 'form was not processed'
            print 'error processing linked_create_form'
            print form.errors
        else:
            pass

    except Exception:
        import traceback
        print traceback.format_exc(5)
        form = traceback.format_exc(5)

    return dict(form=form)
