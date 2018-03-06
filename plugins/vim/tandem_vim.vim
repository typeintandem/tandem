if !has('python')
  " :echom is persistent messaging. See
  " http://learnvimscriptthehardway.stevelosh.com/chapters/01.html
  :echom 'ERROR: Please use a version of Vim with Python support'
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

" Show Session ID for active session
com! TandemSession py tandem_plugin.show_session_id()

" Get the absolute path to the folder this script resides in, respecting
" symlinks
let s:path = fnamemodify(resolve(expand('<sfile>:p')), ':h')

python << EOF

import os
import sys
import vim

# Add the script path to the python path
local_path = vim.eval("s:path")
if local_path not in sys.path:
    sys.path.insert(0, local_path)

import tandem_lib.tandem_plugin as plugin
import tandem_lib.agent.tandem.agent.protocol.messages.editor as m

class TandemVimPlugin:
    def __init__(self):
        self._tandem = plugin.TandemPlugin(
            vim=vim,
            on_start=self._set_up_autocommands,
            message_handler=self._handle_message,
        )
        self._message = None

    def _handle_message(self, message):
        self._message = message
        if isinstance(message, m.ApplyText):
            vim.command(":doautocmd User TandemApplyText")
        elif isinstance(message, m.WriteRequest):
            vim.command(":doautocmd User TandemWriteRequest")
        elif isinstance(message, m.SessionInfo):
            vim.command('echom "Session ID: {}"'.format(message.session_id))
            self._session_id = message.session_id

    def _handle_apply_text(self):
        self._tandem.handle_apply_text(self._message)
        self._message = None

    def _handle_write_request(self):
        self._tandem.handle_write_request(self._message)
        self._message = None

    def _check_buffer(self):
        self._tandem.check_buffer()

    def _set_up_autocommands(self):
        vim.command(':autocmd!')
        vim.command('autocmd TextChanged <buffer> py tandem_plugin._check_buffer()')
        vim.command('autocmd TextChangedI <buffer> py tandem_plugin._check_buffer()')
        vim.command('autocmd VimLeave * py tandem_plugin.stop()')
        vim.command("autocmd User TandemApplyText py tandem_plugin._handle_apply_text()")
        vim.command("autocmd User TandemWriteRequest py tandem_plugin._handle_write_request()")

    def start(self, session_id=None):
        self._tandem.start(session_id)
        self._session_id = session_id

    def stop(self, invoked_from_autocmd=True):
        self._tandem.stop(invoked_from_autocmd)
        self._session_id = None

    def show_session_id(self):
        if not plugin.is_active:
            vim.command(':echom "No instance running."')
            return
        vim.command('echom "Session ID: {}"'.format(self._session_id))


tandem_plugin = TandemVimPlugin()

EOF
