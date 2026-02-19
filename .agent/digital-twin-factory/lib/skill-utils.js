const fs = require('fs');
const path = require('path');
const yaml = require('yaml');

function stripQuotes(value) {
    if (typeof value !== 'string') return value;
    return value.replace(/^['"]|['"]$/g, '').trim();
}

function isPlainObject(value) {
    return value && typeof value === 'object' && !Array.isArray(value);
}

function parseFrontmatter(content) {
    const lines = content.split(/\r?\n/);
    if (!lines.length || lines[0].trim() !== '---') {
        return { data: {}, body: content };
    }

    let endIndex = -1;
    for (let i = 1; i < lines.length; i += 1) {
        if (lines[i].trim() === '---') {
            endIndex = i;
            break;
        }
    }

    if (endIndex === -1) return { data: {}, body: content };

    const fmText = lines.slice(1, endIndex).join('\n');
    let data = {};
    try {
        const doc = yaml.parseDocument(fmText);
        data = doc.toJS();
    } catch (err) {
        data = {};
    }

    return { data, body: lines.slice(endIndex + 1).join('\n') };
}

function readSkill(skillDir, skillId) {
    const skillPath = path.join(skillDir, skillId, 'SKILL.md');
    const content = fs.readFileSync(skillPath, 'utf8');
    const { data } = parseFrontmatter(content);

    return {
        id: skillId,
        name: data.name || skillId,
        description: data.description || '',
        tags: Array.isArray(data.tags) ? data.tags : [],
        path: skillPath,
    };
}

function listSkillIdsRecursive(dir, baseDir = dir, acc = []) {
    const entries = fs.readdirSync(baseDir, { withFileTypes: true });
    for (const entry of entries) {
        if (entry.name.startsWith('.')) continue;
        const fullPath = path.join(baseDir, entry.name);
        if (entry.isDirectory()) {
            const skillFile = path.join(fullPath, 'SKILL.md');
            if (fs.existsSync(skillFile)) {
                acc.push(path.relative(dir, fullPath));
            }
            listSkillIdsRecursive(dir, fullPath, acc);
        }
    }
    return acc.sort();
}

module.exports = {
    listSkillIdsRecursive,
    readSkill,
    parseFrontmatter
};
