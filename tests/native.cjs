const assert=require('node:assert/strict'),fs=require('fs'),vm=require('vm'),path=require('path');
const core=require('../build/zh-core.js');
class Menu { constructor(){this.items=[];} append(item){this.items.push(item);} insert(position,item){this.items.splice(position,0,item);} static buildFromTemplate(template){const menu=new Menu();for(const item of template)menu.append({...item,submenu:Array.isArray(item.submenu)?Menu.buildFromTemplate(item.submenu):item.submenu});return menu;} }
const dialog={showMessageBox(...args){return args},showOpenDialog(...args){return args}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../build/zh-main.cjs'),'utf8'),{require(name){return name==='electron'?{Menu,dialog}:core;}});
const click=()=>42,original={label:'Create Alias',enabled:false,checked:true,id:'repo-alias',click};
const menu=new Menu();menu.append(original);assert.equal(menu.items[0],original);assert.equal(original.label,'创建别名');assert.equal(original.click(),42);assert.equal(original.enabled,false);assert.equal(original.checked,true);assert.equal(original.id,'repo-alias');
menu.insert(0,{label:'Show Worktrees'});assert.equal(menu.items[0].label,'显示工作树');
const template=[{label:'&File',submenu:[{label:'New Worktree...',click}]},{role:'help'}];const built=Menu.buildFromTemplate(template);assert.equal(template[0].label,'&File');assert.equal(built.items[0].label,'文件');assert.match(built.items[0].submenu.items[0].label,/工作树/);assert.equal(built.items[1].label,'帮助');
const options={title:'Delete Worktree',message:'This action cannot be undone.',buttons:['Cancel','Delete'],defaultId:0,cancelId:0,defaultPath:'/tmp/History'};
const window={},ret=dialog.showMessageBox(window,options);assert.equal(ret[0],window);assert.equal(ret[1].title,'删除工作树');assert.equal(ret[1].defaultPath,options.defaultPath);assert.equal(ret[1].cancelId,0);assert.deepEqual([...ret[1].buttons],['取消','删除']);assert.equal(options.title,'Delete Worktree');
assert.equal(core.translate('  Show\n Worktrees  '),'  显示工作树  ');assert.equal(core.translate('Delete tag release-v1'),'删除标签 release-v1');
console.log('PASS native: append/insert/templates/dialogs; callbacks, IDs, states, paths and response ordering preserved');

assert.equal(core.translate('Update from main'),'从 main 更新');
