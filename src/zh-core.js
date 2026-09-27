/* Local UI-only translation helper. No network or credential access. */
(function (root) {
  'use strict';
  const dictionary = __DICTIONARY__;
  const folded = new Map(Object.entries(dictionary).map(([key,value])=>[key.toLowerCase().replace(/\.\.\./g,'…'),value]));
  const templates = __DYNAMIC__.map(([source,target]) => {
    const ids=[];
    const pattern=source.split(/(\{\d+\})/).map(part => {
      if (/^\{\d+\}$/.test(part)) { ids.push(part.slice(1,-1)); return '(.+?)'; }
      return part.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
    }).join('');
    return [new RegExp('^'+pattern+'$','i'),target,ids,/^(?:Confirm Abort|Abort |Begin |Continue |Resolve conflicts before|Resolving conflicts for)|Will Require Force Push/.test(source)];
  });
  function translate(text, dynamic = true) {
    if (typeof text !== 'string' || !text.trim()) return text;
    const key = text.trim().replace(/\s+/g, ' ');
    let value = dictionary[key] || folded.get(key.toLowerCase().replace(/\.\.\./g,'…'));
    if (!value && dynamic) {
      for (const [pattern,target,ids,operation] of templates) {
        const match=key.match(pattern); if(!match)continue;
        const captures=Object.fromEntries(ids.map((id,i)=>[id,operation ? translate(match[i+1],false) : match[i+1]]));
        value=target.replace(/\{(\d+)\}/g,(_,id)=>captures[id]);break;
      }
    }
    if (!value && dynamic) {
      const rules = [
        [/^Current Repository (.+)$/, m => `当前仓库 ${m[1]}`],
        [/^Current Branch (.+)$/, m => `当前分支 ${m[1]}`],
        [/^Commit (\d+) files? to(.*)$/, m => `将 ${m[1]} 个文件提交到${m[2]}`],
        [/^Commit to (.+)$/, m => `提交到 ${m[1]}`],
        [/^(\d+) changed files?$/, m => `${m[1]} 个已更改文件`],
        [/^(\d+) changes?$/, m => `${m[1]} 项更改`],
        [/^Changes (\d+)$/, m => `更改 ${m[1]}`],
        [/^Last fetched (.+)$/, m => `上次获取：${translate(m[1])}`],
        [/^(\d+) minutes? ago$/, m => `${m[1]} 分钟前`],
        [/^(\d+) hours? ago$/, m => `${m[1]} 小时前`],
        [/^(\d+) seconds? ago$/, m => `${m[1]} 秒前`],
        [/^(\d+) days? ago$/, m => `${m[1]} 天前`],
        [/^(\d+) months? ago$/, m => `${m[1]} 个月前`],
        [/^(\d+) years? ago$/, m => `${m[1]} 年前`],
        [/^Fetch origin Last fetched (.+)$/, m => `获取远程更新，上次获取：${translate(m[1])}`],
        [/^(Pull|Push|Fetch|Force push) (.+)$/i, m => `${({'pull':'拉取','push':'推送','fetch':'获取','force push':'强制推送'})[m[1].toLowerCase()]} ${m[2]}`],
        [/^Delete tag (.+)$/, m => `删除标签 ${m[1]}`],
        [/^(Cherry-pick|Squash|Reorder) (\d+) commits?(…|\.\.\.)?$/i, m => `${({'cherry-pick':'摘取','squash':'压缩合并','reorder':'重新排序'})[m[1].toLowerCase()]} ${m[2]} 个提交${m[3]||''}`],
        [/^(.+) in progress$/, m => `${translate(m[1])}正在进行`],
        [/^Resolving conflicts for (.+)$/, m => `正在为${translate(m[1])}解决冲突`],
        [/^Resolve conflicts before (.+)$/, m => `继续${translate(m[1])}前请解决冲突`],
        [/^Open the (.+) website$/, m => `打开 ${m[1]} 网站`],
        [/^Thank you (.+)! 🎉$/, m => `感谢你，${m[1]}！🎉`],
        [/^Current branch is (.+)$/, m => `当前分支为 ${m[1]}`],
        [/^Create (.+) Alias$/, m => `创建 ${m[1]} 别名`],
        [/^Open in (.+)$/, m => `在 ${m[1]} 中打开`],
        [/^Update from (.+)$/, m => `从 ${m[1]} 更新`]
      ];
      for (const [pattern, render] of rules) {
        const match = key.match(pattern);
        if (match) { value = render(match); break; }
      }
    }
    return value ? text.match(/^\s*/)[0] + value + text.match(/\s*$/)[0] : text;
  }
  const api = Object.freeze({ translate, version: '0.2.2', dictionarySize: Object.keys(dictionary).length });
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.DesktopLocalChinese = api;
})(globalThis);
