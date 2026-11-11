import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {analyze} from './engine.mjs';
const cases=JSON.parse(await readFile(new URL('./cases.json',import.meta.url),'utf8'));
for(const [i,c]of cases.entries()){const before=JSON.stringify(c.input);assert.deepEqual(await analyze(c.input),c.expected,'case '+i);assert.equal(JSON.stringify(c.input),before,'must not mutate input');}
for(const invalid of [null,[],42,'invalid'])await assert.rejects(()=>analyze(invalid));
await assert.rejects(()=>analyze(JSON.parse('{"__proto__":{}}')));
console.log(cases.length+' expected-outcome cases and 5 invalid-input cases passed');
