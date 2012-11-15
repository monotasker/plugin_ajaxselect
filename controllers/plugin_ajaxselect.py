from plugin_ajaxselect import AjaxSelect, FilteredAjaxSelect
if 0:
    from gluon import current, dal
    request, session = current.request, current.session
    db = dal.DAL()

def set_widget():
    """
    creates a replacement select widget using the AjaxSelect or
    FilteredAjaxSelect classes and returns the new widget via ajax.
    """
    verbose = 1
    if verbose == 1:
        print '========================================'
        print 'starting controller set_widget()'
    #get variables to build widget for the proper field
    #TODO: Can I get the table from db[field]._table or something like that?
    tablename = request.args[0]
    fieldname = request.args[1]
    if verbose == 1:
        print 'for widget: ||', tablename, '|', fieldname, '||'
    table = db[tablename]
    field = table[fieldname]
    requires = field.requires
    if not isinstance(requires, list):
        requires = [requires]
    else:
        requires = requires

    linktable = requires[0].ktable
    if verbose == 1:
        print 'linked to table |', linktable, '|'

    #get current value of widget
    wrp = request.vars['wrappername']
    if wrp in session and session[wrp] != None:
        value = session[request.vars['wrappername']]
    else:
        valstring = request.vars['value']
        #restore value to list since it was converted to string for url
        value = valstring.split(',')

    if 'rval' in request.vars:
        rval = request.vars['rval']
    else:
        rval = None

    if verbose == 1:
        print 'value:', value

    if request.vars['restricted'] in (None, 'None'):
        w = AjaxSelect().widget(field, value,
            refresher = request.vars['refresher'],
            adder = request.vars['adder'],
            restricted = request.vars['restricted'],
            restrictor = request.vars['restrictor'],
            multi = request.vars['multi'],
            lister = request.vars['lister'],
            sortable = request.vars['sortable'])
    else:
        w = FilteredAjaxSelect().widget(field, value,
            refresher = request.vars['refresher'],
            adder = request.vars['adder'],
            restricted = request.vars['restricted'],
            restrictor = request.vars['restrictor'],
            multi = request.vars['multi'],
            lister = request.vars['lister'],
            sortable = request.vars['sortable'],
            rval = rval)

    return dict(wrapper = w, linktable = linktable, tablename = tablename)

def setval():
    """Called when user changes value of AjaxSelect widget. Stores the current
    widget state in a session object to be used if the widget is refreshed
    before the form is processed."""

    verbose = 1

    theinput = request.args[0]
    wrappername = theinput.replace('_input', '')
    curval = request.vars[theinput]
    if verbose == 1:
        print 'in setval() raw: ', curval

    # error handling to deal with strange occasional conversion of
    #returned val to list
    if type(curval) == list:
        curval = curval[0]
    curval = str(curval).split(',')
    curvalInts = [int(i) for i in curval]
    session[wrappername] = curvalInts

    if verbose == 1:
        print 'in setval() processed: ', curvalInts
        print 'in setval(), session[', wrappername, '=', session[wrappername]

    return curval

def set_form_wrapper():
    """
    Creates the LOAD helper to hold the modal form for creating a new item in
    the linked table
    """
    print 'hi there'
    if len(request.args) > 2:
        form_maker = 'linked_edit_form.load'
    else:
        form_maker = 'linked_create_form.load'

    formwrapper = LOAD('plugin_ajaxselect', form_maker,
                       args = request.args,
                       vars = request.vars,
                       ajax = True)

    return dict(formwrapper = formwrapper)

def linked_edit_form():
    """
    creates a form to edit, update, or delete an intry in the linked table which
    populates the AjaxSelect widget.
    """
    tablename = request.args[0]
    fieldname = request.args[1]
    table = db[tablename]
    field = table[fieldname]
    requires = field.requires
    if not isinstance(requires, list):
        requires = [requires]
    else:
        requires = requires
    linktable = requires[0].ktable

    this_row = request.args[2]
    wrappername = request.vars['wrappername']

    form = SQLFORM(db[linktable], this_row)

    comp_url = URL('plugin_ajaxselect', 'set_widget.load',
                   args = [tablename, fieldname],
                   vars = request.vars)

    if form.process().accepted:
        response.flash = 'form accepted'
        response.js = "web2py_component('%s', '%s');" % (comp_url, wrappername)
    else:
        response.error = 'form was not processed'

    return dict(form = form)

def linked_create_form():
    """
    creates a form to insert a new entry into the linked table which populates
    the ajaxSelect widget
    """

    tablename = request.args[0]
    fieldname = request.args[1]
    wrappername = request.vars['wrappername']
    table = db[tablename]
    field = table[fieldname]

    requires = field.requires
    if not isinstance(requires, list):
        requires = [requires]
    else:
        requires = requires
    linktable = requires[0].ktable

    form = SQLFORM(db[linktable])

    comp_url = URL('plugin_ajaxselect', 'set_widget.load',
                   args = [tablename, fieldname],
                   vars = request.vars)

    if form.process().accepted:
        response.flash = 'form accepted'
        response.js = "web2py_component('%s', '%s');" % (comp_url, wrappername)
    else:
        response.error = 'form was not processed'

    return dict(form = form)
