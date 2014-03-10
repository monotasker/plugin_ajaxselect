// Javascript for the AjaxSelect and related widgets
// part of the plugin_ajaxselect plugin for web2py

//TODO: Bind a separate function to the select if multi=False or no taglist
//when select value is changed, update
function addtag(opt){
    //COMMON get landmarks to navigate dom =====================
    var $p = $(opt).parents('span');
    //get $select, wrappername, $td in info object
    var myinfo = info($p);
    var r_url = geturl(myinfo.$td);

    //add tag for this option to taglist =======================
    var $taglist = $p.find('.taglist');
    var linfo = linkinfo(r_url.url, r_url.vars);
    var newval = $(opt).attr('value');
    var newtext = $(opt).text();
    if($p.hasClass('lister_editlinks')){
        var newtag = editlink(linfo, r_url.args, r_url.vars, newval, newtext);
        $taglist.append(newtag);
    }
    else if($p.hasClass('lister_simple')){
        var newtag = tag(newval, newtext);
        $taglist.append(newtag);
    }
    // FIXME: Shouldn't have to re-bind this here
    $taglist.find('a.tag_remover').on('click', function(event){
        removetag(event.target);
    });
    //make sure newly added tag is added to sortable binding
    $('ul.sortable').sortable('refresh');
    //update select value
    vals = valFromTags($taglist);
    myinfo.$select.val(vals);
    event.preventDefault();
}

function valFromTags($taglist){
    var vals = new Array();
    $taglist.find('li').each(function(){
        var theid = $(this).attr('id');
        vals.push(theid);
    });
    console.log(vals);
    return vals;
}

function whenSortStops($taglist){
    //COMMON get landmarks to navigate dom =====================
    var $p = $taglist.first().parents('span');
    var myinfo = info($p);

    //var vals = valFromTags($taglist);
    var vals = new Array();
    $taglist.each(function(){
        var theid = $(this).attr('id');
        vals.push(theid);
    });
    console.log(vals);
    myinfo.$select.val(vals);

    //reorder options in widget
    for (var i = 0; i < vals.length; i++) {
        var $opts = myinfo.$select.children('option');
        var $opt = myinfo.$select.find('option[value=' + vals[i] + ']');
        console.log(vals[i]);
        $opt.insertAfter($opts.last());
    }
}

//remove an option by clicking on the remover icon in a tag
function removetag(tag){
    //COMMON get landmarks to navigate dom =====================
    var $p = $(tag).parents('span');
    //get $select, wrappername, $theinput, theinput, $td in info object
    var myinfo = info($p);
    var $prnt = $(tag).parent('li');

    //get value of removed option
    var val = $prnt.attr('id');
    //remove option from list of selected values
    $prnt.remove();

    var $taglist = $p.find('.taglist');
    var vals = valFromTags($taglist);
    myinfo.$select.val(vals);

    //var vals = myinfo.$select.val()
    //if (vals.length > 0){
        //var i = vals.indexOf(val);
        //vals.splice(i, 1);
    //}
    ////if the last item is being removed
    //else {
        //myinfo.$select.val(null);
    //}

    event.preventDefault();
}

//constrain and refresh appropriate select widgets if restrictor widget's
//value is changed
$('.restrictor select').on('change', function(event){
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

//utility - determine whether a string contains 'value='
function isValue(x){
    re = /^(?!value=).*$/;
    return String(x).match(re);
}

//utility - get basic landmarks for traversing dom
function info($p){
    var wrappername = $p.attr('id');
    var $select = $p.find('select');
    var $td = $p.parents('li, td');
    return {'wrappername':wrappername, '$select':$select, '$td':$td}
}

//utility - get url, a string with its args, and a string with its vars
function geturl($td){
    var r_url = $td.find('a.refresh_trigger').attr('onclick');
    var url_frag = r_url.match(/set_widget.load(.*)/);
    var url_args_vars = url_frag[1].split('?');
    var url_args = url_args_vars[0];
    var url_vars_raw = url_args_vars[1].split('"')[0];
    var appname = r_url.split('/')[1];
    console.log(url_vars_raw);
    return {'url':r_url, 'args':url_args,
            'vars':url_vars_raw, 'appname':appname}
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

//utility - assemble and return tag with edit link
function editlink(info, args, vars, newval, newtext){
    var link_url = info.linkbase + args + '/';
    link_url += newval + '?' + vars;
    var script_s = "web2py_component('" + link_url + "', '" +
                                        info.formname + "')";
    ntag = '<li class="editlink tag" id="' + newval + '">';
    ntag += '<span class="label label-info">' + newtext + '</span>';
    ntag += '<a id="' + info.linktable + '_editlist_trigger_' + newval + '" ';
    ntag += 'class="edit_trigger editlink tag label label-warning icon-edit" ';
    ntag += 'href="' + link_url + '" ';
    ntag += 'onclick="' + script_s + '; return false;"> </a>';
    ntag += '<a class="tag_remover label label-important icon-remove"> </a>';
    ntag += '</li>';
    return ntag
}

//utility - build and return html for basic tag
function tag(newval, newtext){
    newtag = '<li class="tag" id="' + newval + '">';
    newtag += '<span class="label label-info">' + newtext + '</span>';
    newtag += '<a class="tag tag_remover label label-important icon-remove">&#x200b;</a>';
    newtag += '</li>';

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
