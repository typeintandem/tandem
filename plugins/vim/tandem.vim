if !has('python')
  " :echom is persistent messaging. See
  " http://learnvimscriptthehardway.stevelosh.com/chapters/01.html
  :echom "ERROR: Please use a version of Vim with Python support"
  finish
endif

pyfile tandem.py
