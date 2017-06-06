export default class Action {
  constructor(action, key, target) {
    this.action = action;
    this.key = key;
    this.target = target;
  }

  toString() {
    return `Action: ${this.action}, key: ${this.key}, target: ${this.target}`;
  }
}
