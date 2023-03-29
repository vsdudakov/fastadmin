// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

const matchMedia = () => {
  return {
    matches: false,
    onchange: null,
    addListener: jest.fn(), // Deprecated
    removeListener: jest.fn(), // Deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  };
};

global.matchMedia = global.matchMedia || matchMedia;

if (typeof window.URL.createObjectURL === 'undefined') {
  Object.defineProperty(window.URL, 'createObjectURL', { value: () => undefined });
}

class Worker {
  onmessage: any;
  url: any;

  constructor(stringUrl: string) {
    this.url = stringUrl;
    this.onmessage = () => undefined;
  }

  postMessage(msg: string) {
    this.onmessage(msg);
  }
}
(window as any).Worker = Worker;
