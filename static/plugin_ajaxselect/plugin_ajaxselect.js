//TODO: Continuing bug -- reordering is only saved to db if widget is refreshed before the form is submitted. Maybe the session value isn't being set properly by the selectEnd function?
//TODO: Continuing bug -- changes to the value appear to be reversed after form submission, but clicking on the item in the list (i.e., refreshing the form) makes the changed values appear. Debug output from module suggests that *both* values are coming from the db!!
$('form').live('submit', function(){
    console.log('ouch!');
    //TODO: clear the session value on submit (showing old value)
});

$('.add_trigger').live('click', function(event){
//open modal dialog (using jquery-ui dialog) for adder form
    var the_id = $(this).attr('id');
    var parts = the_id.split('_');
    var linktable = parts[0];

    var dlname = linktable + '_adder_form';
    if($('#' + dlname).length){
        $('#' + dlname).html('').dialog('open');
    } else {
        var newd = $('<div id="' + dlname + '" class="ajaxselect_dialog"></div>');
        newd.dialog({
            autoOpen:false,
            closeOnEscape:false,
            height:600,
            width:700,
            title:'Edit ',
        });
        $('#' + dlname).dialog('open');
    }
    return false
});

$('.edit_trigger').live('click', function(event){
//open modal dialog (using jquery-ui dialog) for edit form
    var the_id = $(this).attr('id');
    var parts = the_id.split('_');
    var linktable = parts[0];
    var dlname = linktable + '_editlist_form';
    if($('#' + dlname).length){
        $('#' + dlname).html('').dialog('open');
    } else {
        var newd = $('<div id="' + dlname + '" class="ajaxselect_dialog"></div>');
        newd.dialog({
            autoOpen:false,
            closeOnEscape:false,
            height:600,
            width:700,
            title:'Edit ',
        });
        $('#' + dlname).dialog('open');
    }

    return false
});

//TODO: Bind a separate function to the select if multi=False or no taglist
//when select value is changed, update
$('.plugin_ajaxselect select[multiple="multiple"] option').live('click', function(event){
    //COMMON get landmarks to navigate dom =====================
    var $p = $(this).parents('span');
    //get $select, wrappername, $theinput, theinput, $td in info object
    var myinfo = info($p);

    //GENERATING NEW VALUE ======================================
    var newval = $(this).val();
    var newtext = $(this).text();
    var theval = myinfo.$theinput.val();
    theval += ',' + newval;

    //COMMON VALUE UPDATING ======================================
    //get url, args, vars, and appname in geturl object
    var r_url = geturl(myinfo.$td);
    //update value in url variables
    var url_vars = update_vars(r_url.vars, theval);
    update_refresher(r_url.url, url_vars, myinfo.wrappername);
    //set the hidden input and select widget to the new value
    myinfo.$theinput.val(theval);
    myinfo.$select.val(theval.split(','));
    //update back end via ajax
    setval(r_url.appname, myinfo.theinput);

    //MODIFY TAG ELEMENTS =========================================
    //set the clicked option to selected
    $(this).attr('selected', 'selected');
    //add tag for this option to taglist
    var $taglist = myinfo.$td.find('.taglist');
    var mylinkinfo = linkinfo(r_url.url, url_vars);
    if($p.hasClass('lister_editlinks')){
        var newtag = editlink(mylinkinfo, r_url.args, url_vars,
                                    newval, newtext);
        $taglist.append(newtag);
    }
    else if($p.hasClass('lister_simple')){
        var newtag = tag(newval, newtext);
        $taglist.append(newtag);
    }
    //make sure newly added tag is added to sortable binding
    $('ul.sortable').sortable('refresh');

    //CLEAN UP ====================================================
    //prevent default behaviour, so that other options aren't de-selected
    return false
});

//TODO: move binding of sortable here from set_widget.load and
//listandedit/edit.load using plugin to provide 'create' event.
function whenSortStops($taglist){
    //COMMON get landmarks to navigate dom =====================
    var $p = $taglist.first().parents('span');
    //get $select, wrappername, $theinput, theinput, $td in info object
    var myinfo = info($p);

    //GENERATING NEW VALUE ======================================
    var vals = new Array();
    $taglist.each(function(){
        var theid = $(this).attr('id');
        vals.push(theid);
    });
    var theval = vals.join(',');

    //COMMON VALUE UPDATING ======================================
    //get url, args, vars, and appname in geturl object
    var r_url = geturl(myinfo.$td);
    //update value in url variables
    var url_vars = update_vars(r_url.vars, theval);
    update_refresher(r_url.url, url_vars, myinfo.wrappername);
    //set hidden input and select widget to the new value
    myinfo.$theinput.val(theval);
    myinfo.$select.val(vals);
    //update back end via ajax
    setval(r_url.appname, myinfo.theinput);

    //reorder options in widget
    for (var i = 0; i < vals.length; i++) {
        var $opts = myinfo.$select.children('option');
        var $opt = myinfo.$select.find('option[value=' + vals[i] + ']');
        console.log(vals[i]);
        console.log($opt.attr('id'));
        $opt.insertAfter($opts.last());
    }
}
//TODO: change values in tag links? in adder link?

//remove an option by clicking on the remover icon in a tag
$('a.tag_remover').live('click', function(event){
    //COMMON get landmarks to navigate dom =====================
    var $p = $(this).parents('span');
    //get $select, wrappername, $theinput, theinput, $td in info object
    var myinfo = info($p);

    //GENERATING NEW VALUE ======================================
    //get value of removed option
    var $prnt = $(this).parent('li');
    var val = $prnt.attr('id');
    //remove option from list of selected values
    var startval = myinfo.$theinput.val()
    var vlist = startval.split(',');
    if (vlist.length > 1){
        var i = vlist.indexOf(val);
        vlist.splice(i, 1);
        var theval = vlist.join();
    }
    //if the last item is being removed
    else {
        var theval = null;
    }

    //COMMON VALUE UPDATING ======================================
    //get url, its arguments, and its variables
    var r_url = geturl(myinfo.$td);
    //update value in url variables and update refresher link
    var url_vars = update_vars(r_url.vars, theval);
    update_refresher(r_url.url, url_vars, myinfo.wrappername);
    //set the hidden input and select widget to the new value
    myinfo.$theinput.val(theval);
    myinfo.$select.val(theval.split(','));
    //update back end via ajax
    setval(r_url.appname, myinfo.theinput);

    //MODIFY TAG ELEMENTS =========================================
    //remove the actual DOM element for the tag
    $prnt.remove();

    //CLEAN UP ====================================================
    //prevent default behaviour so that the link doesn't trigger navigation
    event.preventDefault();
});

$('.restrictor select').live('change', function(event){
//constrain and refresh appropriate select widgets if restrictor widget's
//value is changed
    //get selected value of the restrictor widget to use in constraining the
    //target widget
    var new_val = $(this).find('option:selected').val();

    //get table of the current form from id of restrictor widget
    var parts = $(this).attr('id').split('_');
    var table = parts[0];
    //get field of the restrictor widget, again from its id
    var r_field = parts[1];

    var classlist = $(this).parents('span').attr('class').split(/\s+/);
    var linktable = classlist[1]
    //constrain and refresh each widget with a corresponding 'for_' class on
    //the restrictor widget
    //TODO: add logic in module to insert a for_ class for multiple
    //constrained fields
    $.each(classlist, function(index,item){
       if(item.substring(0,4) == 'for_'){
           //get name of field for widget to be constrained, from the
           //restrictor's classes
           field = item.substring(4);
           //assemble name for span wrapping the widget to be constrained
           var span_id = table + '_' + field + '_loader'
           //assemble url to use for refreshing the constrained widget
           //from url set in modules/plugin_ajaxselect.py for adder
           //this should include the vars (url params) 'fieldval' and
           //'multi'
           var r_url = $('#' + span_id + ' .refresh_trigger').attr('href');
           r_url += '&rval=' + new_val + '&rtable=' + linktable;
           //refresh the widget by refreshing the contents of the wrapper
           //component
           web2py_component(r_url, span_id);
       }
    });
});

//utility - update stored web2py session value via ajax
function setval(appname, inputname){
    ajax('/' + appname + '/plugin_ajaxselect/setval/' + inputname,
                                        ['"' + inputname + '"'], ':eval');
}

//utility - determine whether a string contains 'value='
function isValue(x){
    re = /^(?!value=).*$/;
    return String(x).match(re);
}

//utility - get basic landmarks for traversing dom
function info($p){
    var wrappername = $p.attr('id');
    var $select = $p.find('select');
    var $theinput = $p.find('input');
    var theinput = $theinput.attr('id');
    var $td = $p.parents('li, td');
    return {'wrappername':wrappername, '$select':$select,
            '$theinput':$theinput, 'theinput':theinput, '$td':$td}
}

//utility - get url, a string with its args, and a string with its vars
function geturl($td){
    var r_url = $td.find('a.refresh_trigger').attr('href');
    var url_frag = r_url.match(/set_widget.load(.*)/);
    var url_args_vars = url_frag[1].split('?');
    var url_args = url_args_vars[0];
    var url_vars_raw = url_args_vars[1];
    var appname = r_url.split('/')[1];
    console.log(url_vars_raw);
    return {'url':r_url, 'args':url_args,
            'vars':url_vars_raw, 'appname':appname}
}

//utility - update the 'value' attribute of a vars string
// returns an array with the new vars
function update_vars(vars, val){
    var vlist = vars.split('&');
    vlist = vlist.filter(isValue);
    vlist = vlist.concat('value=' + val);
    vars = vlist.join('&');
    console.log(vars);
    return vars
}

//utility - get misc info from r_url
function linkinfo(url, vlist){
    var appname = url.split('/')[1];
    var linktable_raw = vlist[1];
    var linktable = linktable_raw.replace('linktable=', '');
    var linkbase = '/' + appname;
    linkbase += '/views/plugin_ajaxselect/set_form_wrapper.load';
    var formname = linktable + '_editlist_form';
    return {'linktable':linktable, 'linkbase':linkbase, 'formname':formname}
}

//utility - update the 'value' attribute of refresh_trigger link
function update_refresher(url, vars, wrappername){
    var refresh_url = url.split('?')[0] + '?' + vars;
    $('a.refresh_trigger').attr('href', refresh_url);
    $('a.refresh_trigger').attr('onclick',
            'web2py_component("' + refresh_url + '", "'
            + wrappername + '"); return false;');
    return 'True'
}

//utility - assemble and return tag with edit link
function editlink(info, args, vars, newval, newtext){
    var link_url = info.linkbase + args + '/';
    link_url += newval + '?' + vars;
    var script_s = "web2py_component('" + link_url + "', '" +
                                        info.formname + "')";
    ntag = '<li class="editlink tag" id="' + newval + '">';
    ntag += '<a class="tag_remover">X</a>';
    ntag += '<a id="' + info.linktable + '_editlist_trigger_' + newval + '" ';
    ntag += 'class="edit_trigger editlink tag" ';
    ntag += 'href="' + link_url + '" ';
    ntag += 'onclick="' + script_s + '; return false;">';
    ntag += 'edit' + '</a>';
    ntag += newtext + '</li>';
    return ntag
}

//utility - build and return html for basic tag
function tag(newval, newtext){
    newtag += '<li class="tag" id="' + newval + '">';
    newtag += '<a class="tag_remover">X</a>';
    newtag += '<span>' + newtext + '</span>' + '</li>';
    return newtag
}

//supply .indexOf function to ie browsers before ie8
if (!Array.prototype.indexOf) {
    Array.prototype.indexOf = function (searchElement /*, fromIndex */ ) {
        "use strict";
        if (this == null) {
            throw new TypeError();
        }
        var t = Object(this);
        var len = t.length >>> 0;
        if (len === 0) {
            return -1;
        }
        var n = 0;
        if (arguments.length > 0) {
            n = Number(arguments[1]);
            if (n != n) { // shortcut for verifying if it's NaN
                n = 0;
            } else if (n != 0 && n != Infinity && n != -Infinity) {
                n = (n > 0 || -1) * Math.floor(Math.abs(n));
            }
        }
        if (n >= len) {
            return -1;
        }
        var k = n >= 0 ? n : Math.max(len - Math.abs(n), 0);
        for (; k < len; k++) {
            if (k in t && t[k] === searchElement) {
                return k;
            }
        }
        return -1;
    }
}

// supply .filter() method for arrays in older browsers
if (!Array.prototype.filter)
    {
      Array.prototype.filter = function(fun /*, thisp */)
      {
        "use strict";

        if (this == null)
          throw new TypeError();

        var t = Object(this);
        var len = t.length >>> 0;
        if (typeof fun != "function")
          throw new TypeError();

        var res = [];
        var thisp = arguments[1];
        for (var i = 0; i < len; i++)
        {
          if (i in t)
          {
            var val = t[i]; // in case fun mutates this
            if (fun.call(thisp, val, i, t))
              res.push(val);
          }
        }

        return res;
      };
    }
