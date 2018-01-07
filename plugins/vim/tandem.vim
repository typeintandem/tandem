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

" This needs to live outside the function, otherwise it will include the
" function name in the path ಠ╭╮ಠ
let s:path = fnamemodify(resolve(expand('<sfile>:p')), ':h') . '/tandem.py'
function! Tandem()
  execute 'pyfile ' . s:path
endfunc

" Bind the Tandem function to a globally available command
command! Tandem call Tandem()
