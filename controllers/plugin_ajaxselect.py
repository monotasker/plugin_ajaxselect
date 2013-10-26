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
    #TODO: Can I get the table from db[field]._table or something like that?

    tablename = request.args[0]
    fieldname = request.args[1]
    table = db[tablename]
    field = table[fieldname]
    # FIXME: Since I'm getting link table in widget code, I don't need it here.
    requires = field.requires
    if not isinstance(requires, list):
        requires = [requires]
    linktable = requires[0].ktable

    value = request.vars[fieldname]
    print 'set_widget: value is', value
    rval = request.vars['rval'] if 'rval' in request.vars.keys() else None
    kwargs = {'indx': request.vars['idx'],
              'refresher': request.vars['refresher'],
              'adder': request.vars['adder'],
              'restrictor': request.vars['restrictor'],
              'multi': request.vars['multi'],
              'lister': request.vars['lister'],
              'restricted': request.vars['restricted'],
              'sortable': request.vars['sortable']}

    if request.vars['restricted'] in (None, 'None'):
        w = AjaxSelect(field, value, **kwargs).widget()
    else:
        w = FilteredAjaxSelect(field, value, rval=rval, **kwargs).widget()

    return dict(wrapper=w, linktable=linktable, tablename=tablename)


#def setval():
    #"""Called when user changes value of AjaxSelect widget. Stores the current
    #widget state in a session object to be used if the widget is refreshed
    #before the form is processed."""

    #theinput = request.args[0]
    #wrappername = theinput.replace('_input', '')
    #curval = listcheck(request.vars[theinput])[0]
    #curval = str(curval).split(',')
    #curvalInts = [int(i) for i in curval if i]  # condition for None val
    #session[wrappername] = curvalInts

    #return curval


#def set_form_wrapper():
    #"""
    #Creates the LOAD helper to hold the modal form for creating a new item in
    #the linked table
    #"""
    #if len(request.args) > 2:
        #form_maker = 'linked_edit_form.load'
    #else:
        #form_maker = 'linked_create_form.load'

    #formwrapper = LOAD('plugin_ajaxselect', form_maker,
                       #args=request.args,
                       #vars=request.vars,
                       #ajax=True)

    #return {'formwrapper': formwrapper}


def linked_edit_form():
    """
    creates a form to edit, update, or delete an intry in the linked table which
    populates the AjaxSelect widget.
    """
    tablename = request.args[0]
    fieldname = request.args[1]
    table = db[tablename]
    field = table[fieldname]

    req = field.requires if isinstance(requires, list) else [field.requires]
    linktable = requires[0].ktable

    this_row = request.args[2]
    wrappername = request.vars['wrappername']

    form = SQLFORM(db[linktable], this_row)

    comp_url = URL('plugin_ajaxselect', 'set_widget.load',
                   args=[tablename, fieldname],
                   vars=request.vars)

    if form.process().accepted:
        response.flash = 'form accepted'
        response.js = "web2py_component('%s', '%s');" % (comp_url, wrappername)
    else:
        response.error = 'form was not processed'

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

        form = SQLFORM(db[linktable])

        comp_url = URL('plugin_ajaxselect', 'set_widget.load',
                    args=[tablename, fieldname],
                    vars=request.vars)

        if form.process().accepted:
            response.flash = 'form accepted'
            response.js = "web2py_component('%s', '%s');" % (comp_url, wrappername)
        else:
            response.error = 'form was not processed'
    except Exception:
        import traceback
        print traceback.format_exc(5)
        form = traceback.format_exc(5)

    return dict(form=form)
