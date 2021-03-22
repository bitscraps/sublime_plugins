import sublime
import sublime_plugin
import os
import json
import re
import codecs

from collections import defaultdict
from collections import OrderedDict 

try:
  sublime.edit_storage
except AttributeError:
  sublime.edit_storage = {}

class EditStep:
  def __init__(self, cmd, *args):
    self.cmd = cmd
    self.args = args

  def run(self, view, edit):
    if self.cmd == 'callback':
      return self.args[0](view, edit)

    funcs = {
      'insert': view.insert,
      'erase': view.erase,
      'replace': view.replace,
    }
    func = funcs.get(self.cmd)
    if func:
      func(edit, *self.args)


class Edit:
  defer = defaultdict(dict)

  def __init__(self, view):
    self.view = view
    self.steps = []

  def step(self, cmd, *args):
    step = EditStep(cmd, *args)
    self.steps.append(step)

  def insert(self, point, string):
    self.step('insert', point, string)

  def erase(self, region):
    self.step('erase', region)

  def replace(self, region, string):
    self.step('replace', region, string)

  def callback(self, func):
    self.step('callback', func)

  def run(self, view, edit):
    for step in self.steps:
      step.run(view, edit)

  def __enter__(self):
    return self

  def __exit__(self, type, value, traceback):
    view = self.view
    if sublime.version().startswith('2'):
      edit = view.begin_edit()
      self.run(edit)
      view.end_edit(edit)
    else:
      key = str(hash(tuple(self.steps)))
      sublime.edit_storage[key] = self.run
      view.run_command('apply_edit', {'key': key})


class apply_edit(sublime_plugin.TextCommand):
  def run(self, edit, key):
    sublime.edit_storage.pop(key)(self.view, edit)

class I18nCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    selection =self.view.sel()
    selected_text = self.view.sel()[0]
    text = self.view.substr(self.view.sel()[0])
    file = self.view.file_name();
    filename, file_extension = os.path.splitext(self.view.file_name())

    def on_done(input_string):
      if file_extension == '.tsx':
        escapedtext = re.sub('^[\'|"]', '', text)
        escapedtext2 = re.sub('[\'|"]$', '', escapedtext)

        en_json = codecs.open("/Users/grahamhadgraft/Sites/sofar-client/src/locales/en.json", "r", encoding='utf-8')
        en_json_string = en_json.read()

        myenjson = json.loads(en_json_string)
        myenjson[input_string] = escapedtext2

        en_writable = open("/Users/grahamhadgraft/Sites/sofar-client/src/locales/en.json", "w")
        json.dump(OrderedDict(sorted(myenjson.items())), en_writable, indent=2)

        fd = codecs.open("/Users/grahamhadgraft/Sites/sofar-client/src/locales/es.json", "r", encoding='utf-8')
        data = fd.read()

        myjson = json.loads(data)
        myjson[input_string] = escapedtext2

        f = open("/Users/grahamhadgraft/Sites/sofar-client/src/locales/es.json", "w")
        json.dump(OrderedDict(sorted(myjson.items())), f, indent=2)

        with Edit(self.view) as edit:
          edit.replace(selected_text, 'intl.formatMessage({ id: \''+input_string+'\' })')

        # self.view.run_command('replace_text', { "region": selected_text, "text": "some super stuff" } )
        # self.view.replace(edit, self.view.sel()[0], 'intl.formatMessage({ id: \'{input_string}\' })')

    self.view.window().show_input_panel("Key Name:", "", on_done, None, None)

class I18nReactCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    selection =self.view.sel()
    selected_text = self.view.sel()[0]
    text = self.view.substr(self.view.sel()[0])
    file = self.view.file_name();
    filename, file_extension = os.path.splitext(self.view.file_name())

    def on_done(input_string):
      if file_extension == '.tsx':
        escapedtext = re.sub('^[\'|"]', '', text)
        escapedtext2 = re.sub('[\'|"]$', '', escapedtext)

        en_json = codecs.open("/Users/grahamhadgraft/Sites/sofar-client/src/locales/en.json", "r", encoding='utf-8')
        en_json_string = en_json.read()

        myenjson = json.loads(en_json_string)
        myenjson[input_string] = escapedtext2

        en_writable = open("/Users/grahamhadgraft/Sites/sofar-client/src/locales/en.json", "w")
        json.dump(OrderedDict(sorted(myenjson.items())), en_writable, indent=2)

        fd = codecs.open("/Users/grahamhadgraft/Sites/sofar-client/src/locales/es.json", "r", encoding='utf-8')
        data = fd.read()

        myjson = json.loads(data)
        myjson[input_string] = escapedtext2

        f = open("/Users/grahamhadgraft/Sites/sofar-client/src/locales/es.json", "w")
        json.dump(OrderedDict(sorted(myjson.items())), f, indent=2)

        with Edit(self.view) as edit:
          edit.replace(selected_text, '<FormattedMessage id="'+input_string+'" />')

        # self.view.run_command('replace_text', { "region": selected_text, "text": "some super stuff" } )
        # self.view.replace(edit, self.view.sel()[0], 'intl.formatMessage({ id: \'{input_string}\' })')

    self.view.window().show_input_panel("Key Name:", "", on_done, None, None)
