#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""
Unit tests for the ajaxselect plugin for web2py

run with:
py.test -xvs applications/paideia/plugins/plugin_ajaxselect/tests/
"""

import pytest
#import pprint
from gluon import current
from plugin_ajaxselect import AjaxSelect


@pytest.fixture()
def WIDGET():
    """
    """
    wdg = ['<span class="plugin_ajaxselect tags lister_simple sortable " '
           'id="steps_tags_loader1">'
           '<select class="generic-widget" id="steps_tags" '
           'multiple="multiple" name="tags" size="5">'
           '<option value="1">noun basics</option>'
           '<option value="5">spatial adverbs</option>'
           '<option value="6">nominative 1</option>'
           '<option value="9">verbless clause</option>'
           '<option value="10">present active indicative</option>'
           '<option value="11">future-active-indicative</option>'
           '<option value="12">present-middle-indicative</option>'
           '<option value="13">future middle &amp; passive indicative</option>'
           '<option value="14">μι-conjugation</option>'
           '<option value="15">participle</option>'
           '<option value="16">personal pronouns - genitive-singular</option>'
           '<option value="17">dative 1</option>'
           '<option value="18">accusative 1</option>'
           '<option value="19">present-active-participle</option>'
           '<option value="20">present-middle-passive-participle</option>'
           '<option value="21">aorist-active-participle</option>'
           '<option value="22">aorist-middle-participle</option>'
           '<option value="23">aorist-passive-participle</option>'
           '<option value="24">aorist active indicative</option>'
           '<option value="25">imperfect active indicative</option>'
           '<option value="26">perfect active indicative</option>'
           '<option value="27">pluperfect active indicative</option>'
           '<option value="28">aorist active subjunctive</option>'
           '<option value="29">conjunctions δε, τε, και</option>'
           '<option value="30">simple transitive clauses</option>'
           '<option value="31">prepositional phrases</option>'
           '<option value="32">phrase</option>'
           '<option value="33">preposition basics</option>'
           '<option value="34">relative-pronoun</option>'
           '<option value="36">clause basics</option>'
           '<option value="38">numbers</option>'
           '<option value="39">imperfect-active-indicative</option>'
           '<option value="40">aorist-active-indicative</option>'
           '<option value="41">aorist-middle-indicative</option>'
           '<option value="42">aorist-passive-indicative</option>'
           '<option value="43">irregular-aorist-stem</option>'
           '<option value="44">irregular-perfect-stem</option>'
           '<option value="46">adjectives - predicate vs attributive position</option>'
           '<option value="47">adjectives - substantive use</option>'
           '<option value="48">near demonstrative pronoun</option>'
           '<option value="49">present active infinitive</option>'
           '<option value="50">present middle infinitive</option>'
           '<option value="51">present passive infinitive</option>'
           '<option value="52">aorist-active-infinitive</option>'
           '<option value="53">aorist-middle-infinitive</option>'
           '<option value="54">aorist-passive-infinitive</option>'
           '<option value="55">present active imperative</option>'
           '<option value="56">idiom</option>'
           '<option value="57">imperfect-middle-indicative</option>'
           '<option value="58">imperfect-passive-indicative</option>'
           '<option value="59">compound-clause</option>'
           '<option value="60">infinitive clauses</option>'
           '<option value="61">alphabet-basic</option>'
           '<option value="62">alphabet-intermediate</option>'
           '<option value="63">alphabet-advanced</option>'
           '<option value="64">optative</option>'
           '<option value="65">test1</option>'
           '<option value="66">alphabet-final</option>'
           '<option value="67">questions1_what-who</option>'
           '<option value="68">personal pronouns - nominative - singular</option>'
           '<option value="69">nominative plural nouns &amp; pronouns</option>'
           '<option value="70">default</option>'
           '<option value="71">&#x27;where&#x27; questions</option>'
           '<option value="72">definite article</option>'
           '<option value="73">genitive of relationship</option>'
           '<option value="74">genitive of possession</option>'
           '<option value="75">genitive of source</option>'
           '<option value="76">asking-names</option>'
           '<option value="77">interrogative-pronoun</option>'
           '<option value="79">end of quota</option>'
           '<option value="80">view slides</option>'
           '<option value="81">award badge</option>'
           '<option value="82">nominative 2</option>'
           '<option value="83">nominative 3</option>'
           '<option value="84">dative 2</option>'
           '<option value="85">dative 3</option>'
           '<option value="86">accusative 2</option>'
           '<option value="87">accusative 3</option>'
           '<option value="88">vocabulary - town names</option>'
           '<option value="89">vocabulary - town places</option>'
           '<option value="90">genitive 1</option>'
           '<option value="91">genitive 2</option>'
           '<option value="92">genitive 3</option>'
           '<option value="93">greetings with χαιρειν</option>'
           '<option value="94">far demonstrative pronoun</option>'
           '<option value="95">genitive plural nouns &amp; pronouns</option>'
           '<option value="96">dative plural nouns and pronouns</option>'
           '<option value="97">present middle imperative</option>'
           '<option value="98">infinitive clauses - accusative subject</option>'
           '<option value="99">infinitive clauses direct object</option>'
           '<option value="100">reporting speech</option>'
           '<option value="101">ὁτι clauses</option>'
           '<option value="102">dative of instrument</option>'
           '<option value="103">dative of means</option>'
           '<option value="104">dative of manner</option>'
           '<option value="105">present passive indicative</option>'
           '<option value="106">present passive imperative</option>'
           '<option value="107">dative of agent</option>'
           '<option value="108">δια for agency</option>'
           '<option value="109">genitive of agent</option>'
           '<option value="110">ὑπο for agency</option>'
           '<option value="111">stative clauses with explicit verbs</option>'
           '<option value="112">indefinite subject</option>'
           '<option value="113">making comparisons</option>'
           '<option value="114">vocabulary - colour words</option>'
           '<option value="115">vocabulary - household roles</option>'
           '<option value="116">vocabulary - places and their people</option>'
           '<option value="117">vocabulary - food</option>'
           '<option value="118">vocabulary - common adjectives</option>'
           '<option value="119">vocabulary - 3rd declension stems</option>'
           '<option value="120">vocabulary - ethnic adjectives</option>'
           '<option value="121">vocabulary - verbs of trade</option>'
           '<option value="122">vocabulary - first verbs</option>'
           '<option value="123">vocabulary - speech and thought</option>'
           '<option value="124">vocabulary - temple and cult</option>'
           '<option value="125">vocabulary - action and possibility</option>'
           '<option value="126">vocabulary - crimes and justice</option>'
           '<option value="127">vocabulary - investigating and knowing</option>'
           '<option value="128">contract verbs</option>'
           '<option value="129">accusative plural nouns &amp; pronouns</option>'
           '<option selected="selected" value="2">verb basics</option>'
           '<option selected="selected" value="4">adjective</option>'
           '</select>'
           '<a class="refresh_trigger" data-w2p_disable_with="default" '
           'data-w2p_method="GET" data-w2p_target="steps_tags_loader1" '
           'href="/paideia/plugin_ajaxselect/set_widget.load/steps/tags?'
           'adder=True&amp;indx=1&amp;lister=simple&amp;'
           'multi=basic&amp;refresher=True&amp;restricted=None&amp;'
           'restrictor=None&amp;sortable=True&amp;'
           'value=%7C%2C2%2C%7C%2C4%2C%7C&amp;wrappername=steps_tags_loader1" '
           'id="tags_refresh_trigger" style="">r</a>'
           '<a class="add_trigger" data-w2p_disable_with="default" '
           'data-w2p_method="GET" data-w2p_target="tags_adder_form" '
           'href="/paideia/plugin_ajaxselect/set_form_wrapper.load/steps/tags?'
           'adder=True&amp;indx=1&amp;lister=simple&amp;'
           'multi=basic&amp;refresher=True&amp;restricted=None&amp;'
           'restrictor=None&amp;sortable=True&amp;'
           'value=%7C%2C2%2C%7C%2C4%2C%7C&amp;wrappername=steps_tags_loader1" '
           'id="tags_add_trigger">+</a>'
           '<ul class="taglist sortable">'
           '<li class="tag" id="2">'
           '<a class="tag_remover" data-w2p_disable_with="default">x</a>verb basics</li>'
           '<li class="tag" id="4">'
           '<a class="tag_remover" data-w2p_disable_with="default">x</a>adjective</li>'
           '</ul>'
           '</span>']
    return wdg[0]


@pytest.fixture()
def ADDER():
    """
    """
    addr = ['<a class="add_trigger" data-w2p_disable_with="default" '
            'data-w2p_method="GET" data-w2p_target="tags_adder_form" '
            'href="/paideia/plugin_ajaxselect/set_form_wrapper.load/steps/tags?'
            'adder=True&amp;'
            'indx=1&amp;'
            'lister=simple&amp;'
            'multi=basic&amp;'
            'refresher=True&amp;'
            'restricted=None&amp;'
            'restrictor=None&amp;'
            'sortable=True&amp;'
            'value=%7C%2C2%2C%7C%2C4%2C%7C&amp;'
            'wrappername=steps_tags_loader1" '
            'id="tags_add_trigger">+</a>']
    return addr[0]


@pytest.fixture()
def REFRESHER():
    """
    """
    refr = ['<a class="refresh_trigger" data-w2p_disable_with="default" '
            'data-w2p_method="GET" data-w2p_target="steps_tags_loader1" '
            'href="/paideia/plugin_ajaxselect/set_widget.load/steps/tags?'
            'adder=True&amp;'
            'indx=1&amp;'
            'lister=simple&amp;'
            'multi=basic&amp;'
            'refresher=True&amp;'
            'restricted=None&amp;'
            'restrictor=None&amp;'
            'sortable=True&amp;'
            'value=%7C%2C2%2C%7C%2C4%2C%7C&amp;'
            'wrappername=steps_tags_loader1" id="tags_refresh_trigger" '
            'style="">r</a>']
    return refr[0]


@pytest.fixture()
def SELECT_XML():
    x = ['<select class="generic-widget" id="steps_tags" multiple="multiple" '
         'name="tags" size="5">'
         '<option value="1">noun basics</option>'
         '<option value="5">spatial adverbs</option>'
         '<option value="6">nominative 1</option>'
         '<option value="9">verbless clause</option>'
         '<option value="10">present active indicative</option>'
         '<option value="11">future-active-indicative</option>'
         '<option value="12">present-middle-indicative</option>'
         '<option value="13">future middle &amp; passive indicative</option>'
         '<option value="14">μι-conjugation</option>'
         '<option value="15">participle</option>'
         '<option value="16">personal pronouns - genitive-singular</option>'
         '<option value="17">dative 1</option>'
         '<option value="18">accusative 1</option>'
         '<option value="19">present-active-participle</option>'
         '<option value="20">present-middle-passive-participle</option>'
         '<option value="21">aorist-active-participle</option>'
         '<option value="22">aorist-middle-participle</option>'
         '<option value="23">aorist-passive-participle</option>'
         '<option value="24">aorist active indicative</option>'
         '<option value="25">imperfect active indicative</option>'
         '<option value="26">perfect active indicative</option>'
         '<option value="27">pluperfect active indicative</option>'
         '<option value="28">aorist active subjunctive</option>'
         '<option value="29">conjunctions δε, τε, και</option>'
         '<option value="30">simple transitive clauses</option>'
         '<option value="31">prepositional phrases</option>'
         '<option value="32">phrase</option>'
         '<option value="33">preposition basics</option>'
         '<option value="34">relative-pronoun</option>'
         '<option value="36">clause basics</option>'
         '<option value="38">numbers</option>'
         '<option value="39">imperfect-active-indicative</option>'
         '<option value="40">aorist-active-indicative</option>'
         '<option value="41">aorist-middle-indicative</option>'
         '<option value="42">aorist-passive-indicative</option>'
         '<option value="43">irregular-aorist-stem</option>'
         '<option value="44">irregular-perfect-stem</option>'
         '<option value="46">adjectives - predicate vs attributive position</option>'
         '<option value="47">adjectives - substantive use</option>'
         '<option value="48">near demonstrative pronoun</option>'
         '<option value="49">present active infinitive</option>'
         '<option value="50">present middle infinitive</option>'
         '<option value="51">present passive infinitive</option>'
         '<option value="52">aorist-active-infinitive</option>'
         '<option value="53">aorist-middle-infinitive</option>'
         '<option value="54">aorist-passive-infinitive</option>'
         '<option value="55">present active imperative</option>'
         '<option value="56">idiom</option>'
         '<option value="57">imperfect-middle-indicative</option>'
         '<option value="58">imperfect-passive-indicative</option>'
         '<option value="59">compound-clause</option>'
         '<option value="60">infinitive clauses</option>'
         '<option value="61">alphabet-basic</option>'
         '<option value="62">alphabet-intermediate</option>'
         '<option value="63">alphabet-advanced</option>'
         '<option value="64">optative</option>'
         '<option value="65">test1</option>'
         '<option value="66">alphabet-final</option>'
         '<option value="67">questions1_what-who</option>'
         '<option value="68">personal pronouns - nominative - singular</option>'
         '<option value="69">nominative plural nouns &amp; pronouns</option>'
         '<option value="70">default</option>'
         '<option value="71">&#x27;where&#x27; questions</option>'
         '<option value="72">definite article</option>'
         '<option value="73">genitive of relationship</option>'
         '<option value="74">genitive of possession</option>'
         '<option value="75">genitive of source</option>'
         '<option value="76">asking-names</option>'
         '<option value="77">interrogative-pronoun</option>'
         '<option value="79">end of quota</option>'
         '<option value="80">view slides</option>'
         '<option value="81">award badge</option>'
         '<option value="82">nominative 2</option>'
         '<option value="83">nominative 3</option>'
         '<option value="84">dative 2</option>'
         '<option value="85">dative 3</option>'
         '<option value="86">accusative 2</option>'
         '<option value="87">accusative 3</option>'
         '<option value="88">vocabulary - town names</option>'
         '<option value="89">vocabulary - town places</option>'
         '<option value="90">genitive 1</option>'
         '<option value="91">genitive 2</option>'
         '<option value="92">genitive 3</option>'
         '<option value="93">greetings with χαιρειν</option>'
         '<option value="94">far demonstrative pronoun</option>'
         '<option value="95">genitive plural nouns &amp; pronouns</option>'
         '<option value="96">dative plural nouns and pronouns</option>'
         '<option value="97">present middle imperative</option>'
         '<option value="98">infinitive clauses - accusative subject</option>'
         '<option value="99">infinitive clauses direct object</option>'
         '<option value="100">reporting speech</option>'
         '<option value="101">ὁτι clauses</option>'
         '<option value="102">dative of instrument</option>'
         '<option value="103">dative of means</option>'
         '<option value="104">dative of manner</option>'
         '<option value="105">present passive indicative</option>'
         '<option value="106">present passive imperative</option>'
         '<option value="107">dative of agent</option>'
         '<option value="108">δια for agency</option>'
         '<option value="109">genitive of agent</option>'
         '<option value="110">ὑπο for agency</option>'
         '<option value="111">stative clauses with explicit verbs</option>'
         '<option value="112">indefinite subject</option>'
         '<option value="113">making comparisons</option>'
         '<option value="114">vocabulary - colour words</option>'
         '<option value="115">vocabulary - household roles</option>'
         '<option value="116">vocabulary - places and their people</option>'
         '<option value="117">vocabulary - food</option>'
         '<option value="118">vocabulary - common adjectives</option>'
         '<option value="119">vocabulary - 3rd declension stems</option>'
         '<option value="120">vocabulary - ethnic adjectives</option>'
         '<option value="121">vocabulary - verbs of trade</option>'
         '<option value="122">vocabulary - first verbs</option>'
         '<option value="123">vocabulary - speech and thought</option>'
         '<option value="124">vocabulary - temple and cult</option>'
         '<option value="125">vocabulary - action and possibility</option>'
         '<option value="126">vocabulary - crimes and justice</option>'
         '<option value="127">vocabulary - investigating and knowing</option>'
         '<option value="128">contract verbs</option>'
         '<option value="129">accusative plural nouns &amp; pronouns</option>'
         '<option selected="selected" value="2">verb basics</option>'
         '<option selected="selected" value="4">adjective</option>'
         '</select>']
    return x[0]


@pytest.fixture()
def FIELD(db):
    f = db.steps.tags
    return f


@pytest.fixture()
def FIELDSET(FIELD):
    fs = str(FIELD).split('.')
    return fs


@pytest.fixture()
def myselect(FIELD):
    """
    """
    return AjaxSelect(FIELD, '|2|4|', indx=1, multi='basic', lister='simple',
                      refresher=True, sortable=True)


class TestAjaxSelect():
    """
    Unit testing class for the ajaxselect widget code.
    """
    def test_get_wrappername(self, myselect, FIELDSET):
        """
        """
        wname = myselect.get_wrappername(FIELDSET)
        assert wname == 'steps_tags_loader1'

    def test_get_linktable(self, myselect, FIELD):
        """
        """
        lt = myselect.get_linktable(FIELD)
        assert lt == 'tags'

    def test_choose_val(self, myselect, FIELDSET):
        """
        """
        session = current.session

        # without session value present
        if 'steps_tags_loader1' in session.keys():
            del session['steps_tags_loader1']
        myval = myselect.choose_val([2, 4])
        assert myval == [2, 4]

        # with session value present but null
        session['steps_tags_loader1'] = None
        myval = myselect.choose_val([2, 4])
        assert myval == [2, 4]

        # with session value present
        session['steps_tags_loader1'] = [3, 6]
        myval = myselect.choose_val([2, 4])
        assert myval == [3, 6]

    def test_sanitize_int_list(self, myselect):
        """
        """
        assert myselect.sanitize_int_list(2) == [2]
        assert myselect.sanitize_int_list('') == None
        assert myselect.sanitize_int_list([]) == None
        assert myselect.sanitize_int_list('2') == [2]
        assert myselect.sanitize_int_list([2]) == [2]
        assert myselect.sanitize_int_list([2, 4]) == [2, 4]
        assert myselect.sanitize_int_list('|2|4|') == [2, 4]
        assert myselect.sanitize_int_list('|2|') == [2]
        assert myselect.sanitize_int_list(['2', 4, None, '']) == [2, 4]

    def test_get_classes(self, myselect):
        """
        """
        vars = [['tags', 'badges', 'paths', 'simple', True],
                ['tags', None, None, 'editlinks', False]]
        outs = ['plugin_ajaxselect tags restrictor_for_paths '
                'restricted_by_badges lister_simple sortable ',
                'plugin_ajaxselect tags lister_editlinks ']
        for n in range(0, len(vars)):
            classes = myselect.get_classes(*vars[n])
            assert classes == outs[n]

    def test_create_widget(self, myselect, SELECT_XML):
        """
        """
        widg = myselect.create_widget().xml()
        widg.decode('string_escape').decode('utf-8')
        assert widg == SELECT_XML

    def test_make_refresher(self, myselect, REFRESHER):
        """
        """
        wname = myselect.wrappername
        linktable = myselect.linktable
        uargs = myselect.uargs
        uvars = myselect.uvars
        refr = myselect.make_refresher(wname, linktable, uargs, uvars)
        assert refr.xml() == REFRESHER

    def test_make_adder(self, myselect, ADDER):
        """
        """
        wname = myselect.wrappername
        linktable = myselect.linktable
        adder = myselect.make_adder(wname, linktable)
        assert adder.xml() == ADDER

    def test_make_taglist(self, myselect):
        """
        """
        taglist = ['<ul class="taglist sortable">'
                   '<li class="tag" id="2">'
                   '<a class="tag_remover" data-w2p_disable_with="default">x'
                   '</a>verb basics</li>'
                   '<li class="tag" id="4">'
                   '<a class="tag_remover" data-w2p_disable_with="default">x'
                   '</a>adjective</li>'
                   '</ul>']
        tlist = myselect.make_taglist()
        assert tlist.xml() == taglist[0]

    def test_make_linklist(self, myselect):
        """
        """
        # TODO: write test code
        pass

    def test_get_widget_index(self, myselect):
        """
        """
        assert myselect.get_widget_index() == 1

    def test_restrict(self, myselect):
        """
        """
        # TODO: write test code
        pass

    def test_widget(self, myselect, WIDGET):
        """
        """
        widg = myselect.widget().xml()
        widg.decode('string_escape').decode('utf-8')
        assert widg == WIDGET


class TestAjaxSelectController():
    """
    Unit testing class for controllers/plugin_ajaxselect.py
    """
    def test_set_widget(self, web2py):
        c = web2py.controllers.plugin_ajaxselect
        new_widg = c.set_widget().xml()
        oldval = 'value=%7C%2C2%2C%7C%2C4%2C%7C&amp;'
        newval = 'value=%7C%2C2%2C%7C%2C4%2C%7C&amp;'
        assert new_widg == WIDGET.replace(oldval, newval)  # FIXME: broken
