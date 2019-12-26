import sublime
import sublime_plugin
import math
import json
from urllib.request import urlopen

def CrateVersions(name):
    url = 'https://crates.io/api/v1/crates/{}/versions'.format(name)
    resp = urlopen(url)
    parsed = json.loads(resp.read().decode("utf-8"))

    versions = []
    for obj in parsed["versions"]:
        if not obj["yanked"]: versions.append(obj["num"])

    return versions

class CrateVersionInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self, view, crate, versions):
        self.view = view
        self.crate = crate
        self.versions = versions

    def placeholder(self):
        return "crate version (e.g. 0.3.2, 1.0.104)"

    def list_items(self):
        return self.versions

    def preview(self, version):
        return '{} = "{}"'.format(self.crate, version)

    def validate(self, version):
        return True

class CrateNameInputHandler(sublime_plugin.TextInputHandler):
    def __init__(self, view):
        self.view = view

    def placeholder(self):
        return "crate name (e.g. serde, rayon)"

    def next_input(self, args):
        crate = args['crate_name']
        versions = CrateVersions(crate)
        return CrateVersionInputHandler(self.view, crate, versions)

    def validate(self, expr):
        return True

class InsertCrateCommand(sublime_plugin.TextCommand):
    def run(self, edit, crate_name, crate_version):
        dependency = '{} = "{}"'.format(crate_name, crate_version)
        for region in self.view.sel():
            self.view.insert(edit, region.end(), dependency)

    def input(self, args):
        return CrateNameInputHandler(self.view)

class FetchCratesVersionsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            string = ""

            lines = self.view.substr(region)
            for line in lines.splitlines():
                crate = line.strip()
                if crate:
                    try:
                        version = CrateVersions(crate)[0]
                        string += '{} = "{}"'.format(crate, version)
                    except:
                        string += line
                string += '\n'

            self.view.replace(edit, region, string)
