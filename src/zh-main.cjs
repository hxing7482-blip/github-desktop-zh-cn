'use strict';
const { Menu } = require('electron');
const { translate } = require('./zh-core.js');
const build = Menu.buildFromTemplate;
const roles = {services:'服务',hide:'隐藏 GitHub Desktop',hideOthers:'隐藏其他应用',unhide:'全部显示',quit:'退出 GitHub Desktop',minimize:'最小化',close:'关闭窗口',window:'窗口',windowMenu:'窗口',help:'帮助',editMenu:'编辑'};
function localize(template) {
  return template.map(item => {
    if (!item || typeof item !== 'object') return item;
    const copy = {...item};
    if (typeof copy.label === 'string') copy.label = translate(copy.label.replace(/&/g,''));
    else if (roles[copy.role]) copy.label = roles[copy.role];
    if (Array.isArray(copy.submenu)) copy.submenu = localize(copy.submenu);
    return copy;
  });
}
Menu.buildFromTemplate = function (template) { return build.call(this, localize(template)); };
// Context menus construct MenuItem directly instead of using buildFromTemplate.
// Translate before native insertion; keep original items, IDs, callbacks and states.
function localizeItem(item) {
  if (item && typeof item.label === 'string') item.label = translate(item.label.replace(/&/g,''));
  return item;
}
const append = Menu.prototype.append;
const insert = Menu.prototype.insert;
Menu.prototype.append = function(item) { return append.call(this, localizeItem(item)); };
Menu.prototype.insert = function(position,item) { return insert.call(this, position, localizeItem(item)); };
// Localize native dialog captions only; leave paths, options and responses intact.
const { dialog } = require('electron');
for (const name of ['showMessageBox','showMessageBoxSync','showOpenDialog','showOpenDialogSync','showSaveDialog','showSaveDialogSync']) {
  const original = dialog[name];
  if (typeof original !== 'function') continue;
  dialog[name] = function(...args) {
    const position = args.length > 1 && args[1] && typeof args[1] === 'object' ? 1 : 0;
    const options = args[position];
    if (options && typeof options === 'object') {
      const translated = {...options};
      for (const key of ['title','message','detail','buttonLabel','checkboxLabel','nameFieldLabel']) {
        if (typeof translated[key] === 'string') translated[key] = translate(translated[key]);
      }
      if (Array.isArray(translated.buttons)) translated.buttons = translated.buttons.map(label => translate(label));
      args[position] = translated;
    }
    return original.apply(this,args);
  };
}
