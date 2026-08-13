import { readFileSync } from 'node:fs';

const inventory = JSON.parse(readFileSync(new URL('../reference-inventory.json', import.meta.url), 'utf8'));

const role = {
  name: 'gecode-api',
  body: { type: String, required: true },
  run(data) {
    const key = data.body.trim();
    const object = inventory.objects[key];
    if (!object) throw new Error(`Unknown Gecode ${inventory.gecode_version} API symbol: ${key}`);
    return [{
      type: 'link',
      url: `${inventory.base_url}${object.url}`,
      title: `${object.title} (Gecode ${inventory.gecode_version} reference)`,
      class: 'gecode-api',
      children: [{ type: 'inlineCode', value: object.title }],
    }];
  },
};

export default { name: 'Gecode release inventory', roles: [role] };
