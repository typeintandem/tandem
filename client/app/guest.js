/* global Node */
/* global window */
import { ipcRenderer } from 'electron';
import constants from './constants';

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
    ipcRenderer.sendToHost(constants.RecorderWebView.EventType.KEYUP, e.key);
  });
  window.addEventListener('click', (e) => {
    const el = findElement(e.target);
    if (el == null) return;
    ipcRenderer.sendToHost(constants.RecorderWebView.EventType.CLICK, e.button, el.tagName,
      el.id, el.className, el.textContent);
  });
  ipcRenderer.sendToHost(constants.RecorderWebView.EventType.READY, '--- Event hooks attached ---');
};
