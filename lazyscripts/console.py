#!/usr/bin/env python
# -*- encoding=utf8 -*-
#
# Copyright © 2010 Hsin Yi Chen
#
# Lazyscripts is a free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This software is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this software; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA
import cmd
import os
import optparse
import sys

from lazyscripts import command as lzscmd
from lazyscripts import distro
from lazyscripts import pool as lzspool
from lazyscripts import env

class LzsAdmin(cmd.Cmd):

    #{{{def __init__(self):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.curdir = os.path.abspath(os.path.curdir)
    #}}}

    def do_update(self, lines):
        print "building scripts index..."
        self._build_scripts_index()

    #{{{def _build_scripts_index(self):
    def _build_scripts_index(self):
        root = env.resource_name('pools')
        contents = []
        for poolname in os.listdir(root):
            poolpath = os.path.join(root, poolname)
            pool = lzspool.ScriptsPool(poolpath)
            for cat, scripts in pool.scripts(None, env.get_local()).items():
                if not scripts: continue
                for script in scripts:
                    contents.append("%s/%s/%s - %s " % (poolname, cat, script.id, script.name))

        index_path = os.path.join(env.resource_name('caches'), 'SCRIPTS_INDEX')
        with open(index_path, 'w') as f:
            f.write("\n".join(contents+['']))
    #}}}

    def do_search(self, lines):
        index_path = os.path.join(env.resource_name('caches'), 'SCRIPTS_INDEX')
        os.system("grep %s %s" % (lines, index_path))

    def do_script(self, lines):
        lzscmd.ScriptCmd(lines).execute(self.curdir)

    def do_pool(self, lines):
        lzscmd.PoolCmd(lines).execute(self.curdir)

    def do_gui(self, lines):
        lzscmd.GuiCmd(lines).execute(self.curdir)

#{{{def run(args=None):
def run(args=None):
    if not args:
        args = sys.argv[1:]

    argc = len(args)
    if argc < 1:
        print "USAGE:\n\t...TBD..."
        sys.exit()

    env.register_workspace()
    env.prepare_runtimeenv()

    admin = LzsAdmin()
    admin.onecmd(' '.join(args))
#}}}

#{{{def gui_run():
def gui_run():
    if os.getuid() == 0:
        print "please do not run as root."
        sys.exit()

    env.register_workspace()
    env.prepare_runtimeenv()
    env.storageenv()
    dist = distro.Distribution().name
    if not dist:
        print "distrobution no supported."
        sys.exit()

    # argument process.
    message_sudo="\"執行'Lazyscripts 懶人包' 會修改系統設定，並會安裝新軟體，所以需要系統管理員權限。 請輸入系統管理密碼，才能繼續執行。(在 Lazyscripts 下，預設這就是你登入系統時所用的密碼。)\""

    prefix = 'gksu --message %s' % message_sudo

    parser = optparse.OptionParser()
    parser.add_option("-a", "--autosync",
		action="store_true",
                  dest="autosync",
                  default=False,
                  help="sync scripts pool automatically")
    parser.add_option("-s", "--selection",
                  dest="selection_list")
    parser.add_option("-r", "--rev",
                  dest="rev")
    (options, args) = parser.parse_args()

    if options.autosync:
      if not options.rev:
          cmd = "lzs pool sync"
      else:
          cmd = "lzs pool sync --rev %s" % options.rev
      #@FIXME show the progress dialog with fake progress status.
      progress_dialog_cmd = [
          "zenity --progress --title='Lazyscripts'",
          "--text='Downloading scripts...'",
          "--percentage=80" ,
          "--auto-close --auto-kill",
          "--width=400"]
      os.system("%s | %s" % (cmd, ' '.join(progress_dialog_cmd)))

    if options.selection_list:
        cmd = "%s lzs gui run %s" % (prefix, options.selection_list)
    else:
        cmd = "%s lzs gui run" % prefix
    os.system(cmd)
#}}}
