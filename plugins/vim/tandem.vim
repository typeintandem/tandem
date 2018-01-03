if !has('python')
  " :echom is persistent messaging. See
  " http://learnvimscriptthehardway.stevelosh.com/chapters/01.html
  :echom "ERROR: Please use a version of Vim with Python support"
  finish
endif

if !executable('python3')
  :echom "ERROR: Global python3 install required."
  finish
endif

" TODO: Use file path relative to .vim file
pyfile tandem.py
