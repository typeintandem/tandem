/* global Node */
/* global window */
import { ipcRenderer } from 'electron';

const findElement = (node) => {
  let curr = node;
  while (curr != null) {
    if (curr.nodeType === Node.ELEMENT_NODE && (!!curr.id || !!curr.className)) {
      return curr;
    }
    curr = curr.parentNode;
  }
  return null;
};

window.attachHooks = () => {
  window.addEventListener('keyup', (e) => {
    ipcRenderer.sendToHost('KEYUP', e.key);
  });
  window.addEventListener('click', (e) => {
    const el = findElement(e.target);
    if (el == null) return;
    ipcRenderer.sendToHost('CLICK', e.button, el.tagName, el.id, el.class);
  });
  ipcRenderer.sendToHost('READY', '--- Event hooks attached ---');
};
