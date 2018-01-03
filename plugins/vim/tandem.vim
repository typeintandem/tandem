if !has('python')
  " :echom is persistent messaging. See
  " http://learnvimscriptthehardway.stevelosh.com/chapters/01.html
  :echom "ERROR: Please use a version of Vim with Python support"
  finish
endif

" TODO: Perform a check for a global python3 install (required).
" TODO: Use file path relative to .vim file
pyfile tandem.py
