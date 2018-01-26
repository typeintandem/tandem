if !has('python')
  " :echom is persistent messaging. See
  " http://learnvimscriptthehardway.stevelosh.com/chapters/01.html
  :echom 'ERROR: Please use a version of Neovim with Python support'
  finish
endif

if !executable('python3')
  :echom 'ERROR: Global python3 install required.'
  finish
endif

" Bind the Tandem functions to globally available commands.
" =================
" Start agent with `:Tandem`
" Start agent and connect to network with `:Tandem <localhost | ip> <port>`
com! -nargs=* Tandem py tandem_plugin.start(<f-args>)
" ================
" Stop agent (and disconnect from network) with `:TandemStop`
com! TandemStop py tandem_plugin.stop(False)

python << EOF

import os
import sys
from threading import Event
import vim

# For now, add the tandem agent path to the system path so that we can use the
# existing messages protocol implementation
tandem_agent_path = os.path.abspath('../../agent')
if tandem_agent_path not in sys.path:
    sys.path.insert(0, tandem_agent_path)
local_path = os.path.abspath('./')
if local_path not in sys.path:
    sys.path.insert(0, local_path)

import tandem_lib as tandem
import tandem.protocol.editor.messages as m

class TandemNeovimPlugin:
    def __init__(self):
        self._tandem = tandem.TandemPlugin(
            self._set_up_autocommands,
            self._handle_message,
            self._check_buffer,
        )
        self._text_applied = Event()

    def _set_up_autocommands(self):
        vim.command(':autocmd!')
        vim.command('autocmd TextChanged <buffer> py tandem_plugin._check_buffer()')
        vim.command('autocmd TextChangedI <buffer> py tandem_plugin._check_buffer()')
        vim.command('autocmd VimLeave * py tandem_plugin.stop()')

    def _handle_message(self, message):
        if isinstance(message, m.ApplyText):
            vim.async_call(self._tandem.handle_apply_text, message)
        elif isinstance(message, m.WriteRequest):
            self._text_applied.clear()
            vim.async_call(self._tandem.handle_write_request, message, lambda: self._text_applied.set())
            self._text_applied.wait()

    def _check_buffer(self):
        vim.async_call(self._tandem.check_buffer)

    def start(self, host_ip=None, host_port=None):
        self._tandem.start(host_ip, host_port)

    def stop(self, invoked_from_autocmd=True):
        self._tandem.stop(invoked_from_autocmd)

tandem_plugin = TandemNeovimPlugin()

EOF
