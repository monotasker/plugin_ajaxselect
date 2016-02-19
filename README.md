README for plugin_ajaxselect, a widget plugin for the web2py web development framework
version 0.8 (beta)
Developed by Ian W. Scott (monotasker), scottianw@gmail.com
Copyright Ian W. Scott, 2012.
Licensed under the GNU General Public License v. 3 (http://www.gnu.org/copyleft/gpl.html)

## Overview

This plugin creates a select widget wrapped that can be refreshed via ajax without resetting the entire form. It also provides an "add new" button that allows users to add a new item to the table that populates the select widget via ajax. The widget is then automatically refreshed via ajax so that the new item is visible as a select option and can be chosen. All of this happens without a page or form refresh so that data entered in other fields is not lost or submitted.

## Dependencies

|------------|----------------------|
| jquery-ui  | 'sortable' module used for reordering of selected values in the value list |
| bootstrap3 | 'modal' javascript module used for the modal windows to hold forms that create and edit values |

## Installation

1. download the plugin file;
2. In the web2py online ide (design view for your app) scroll to the bottom section labeled "Plugins"; 
3. At the bottom of that section is a widget to "upload plugin file". Click "Browse".
4. In the file selection window that opens, navigate to the downloaded plugin file, select it, and click "open". The file selection window should close.
5. Click the "upload" button.

The plugin should now be installed and ready to use.

## Usage
In a web2py model file, import this class and then apply it as the widget-factory for one or more db fields. To do this for a field named 'author' from a table named 'notes' you would add this line somewhere in the model file:

    db.notes.author.widget = lambda field, value: AjaxSelect(field, value, 'authors', {optional argument}).widget()

Note that the third argument passed to AjaxSelect should be the name of the able *referenced by the current field*. In this example, the field 'author' references the table 'authors'. So the third argument in this case is 'authors'.

### Optional arguments:

**refresher** (True/False; defaults to True): If True, this provides a button to manually refresh the select
widget via ajax. If set to False, the widget is still refreshed via ajax (automatically), but the button to do it manually is removed.

**adder** (True/False; defaults to True): If True, a button is provided to add a new record to the linked table that populates the select widget. The adding form is presented in a bootstrap3 modal.

**restricted** ({fieldname}; defaults to None): adds a dynamic constraint on the records displayed in the select widget. When the specified form field (within the same form) has its value changed, this select will be refreshed and its displayed records filtered accordingly. Note that this is only useful if {fieldname} references values shared with the linked table.

**restrictor** ({fieldname}; defaults to None): makes this select widget acts as a constraint on the content of another select widget in the same table. When the value of this select is changed, the available values in the {fieldname} widget will be filtered and that widget updated via ajax.

**multi** (True/False; defaults to False): If True the widget is a multi-select. If false it's a simple single select.

**lister** ('simple'/'editlinks'/False): If 'simple,' a dynamic list of selected values is created below the select. If 'editlinks' is set this list of values will include an 'edit' link with each value. Clicking that edit link will open a modal form for editing the given record on the linked table.

**sortable** (True/False; defaults to False): If True (and 'lister' is not False) allows drag-and-drop reordering of the selected values in the list below the select. (Depends on jquery-ui sortable plugin.)

**orderby** ({fieldname}; defaults to None): Determines field (in the linked table) by which to order the options in the select widget.
