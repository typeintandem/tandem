'use babel';

import { CompositeDisposable, Disposable } from 'atom';

const makeButton = (text, callback) => {
  const button = document.createElement('button');
  button.classList.add('btn');
  button.textContent = text;
  button.addEventListener('click', callback);
  return button;
};

export default class ConnectView {
  constructor(connectCallback, closeCallback) {
    this._element = document.createElement('div');
    this._element.classList.add('tandem-connect-view');

    const label = document.createElement('div');
    const labelText = document.createElement('span');
    labelText.textContent = 'Enter an IP and port (e.g. localhost 12345)';
    label.appendChild(labelText);
    this._element.appendChild(label);

    const input = document.createElement('input');
    input.classList.add('input-text');
    this._element.appendChild(input);

    const okButtonCallback = () => {
      connectCallback(input.value);
      input.value = '';
    };
    const okButton = makeButton('Connect', okButtonCallback);

    const cancelButtonCallback = () => {
      closeCallback();
      input.value = '';
    };
    const cancelButton = makeButton('Cancel', cancelButtonCallback);

    this._element.appendChild(okButton);
    this._element.appendChild(cancelButton);

    this._subscriptions = new CompositeDisposable();
    this._subscriptions.add(new Disposable(() => {
      okButton.removeEventListener('click', okButtonCallback);
      cancelButton.removeEventListener('click', cancelButtonCallback);
    }));
  }

  destroy() {
    this.subscriptions.dispose();
    this._element.remove();
  }

  getElement() {
    return this._element;
  }
}
