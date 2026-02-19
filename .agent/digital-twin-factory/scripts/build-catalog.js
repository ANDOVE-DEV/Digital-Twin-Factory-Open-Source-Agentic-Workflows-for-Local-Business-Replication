const fs = require('fs');
const path = require('path');
const {
    listSkillIdsRecursive,
    readSkill,
    tokenize,
    unique,
} = require('../lib/skill-utils');

const ROOT = path.resolve(__dirname, '..');
const SKILLS_DIR = path.join(ROOT, 'skills');

// Simple stopwords list
const STOPWORDS = new Set([
    'a', 'an', 'and', 'the', 'is', 'in', 'at', 'of', 'or', 'for', 'with', 'to', 'use', 'when'
]);

function deriveTags(skill) {
    let tags = Array.isArray(skill.tags) ? skill.tags : [];
    tags = tags.map(tag => tag.toLowerCase()).filter(Boolean);
    return tags;
}

function renderCatalogMarkdown(catalog) {
    const lines = [];
    lines.push('# Factory Skill Catalog');
    lines.push('');
    lines.push(`Generated at: ${catalog.generatedAt}`);
    lines.push('');
    lines.push(`Total skills: ${catalog.total}`);
    lines.push('');
    lines.push('| Skill | Description | Tags |');
    lines.push('| --- | --- | --- |');

    for (const skill of catalog.skills) {
        const description = (skill.description || '').replace(/\|/g, '\\|');
        const tags = skill.tags.join(', ');
        lines.push(`| \`${skill.id}\` | ${description} | ${tags} |`);
    }

    return lines.join('\n');
}

function buildCatalog() {
    // Ensure skills dir exists
    if (!fs.existsSync(SKILLS_DIR)) {
        console.log("Skills directory not found, skipping catalog build.");
        return;
    }

    const skillRelPaths = listSkillIdsRecursive(SKILLS_DIR);
    const skills = skillRelPaths.map(relPath => readSkill(SKILLS_DIR, relPath));
    const catalogSkills = [];

    for (const skill of skills) {
        const tags = deriveTags(skill);
        catalogSkills.push({
            id: skill.id,
            name: skill.name,
            description: skill.description,
            tags,
            path: path.relative(ROOT, skill.path),
        });
    }

    const catalog = {
        generatedAt: new Date().toISOString(),
        total: catalogSkills.length,
        skills: catalogSkills.sort((a, b) => a.id.localeCompare(b.id)),
    };

    const catalogMarkdownPath = path.join(ROOT, 'CATALOG.md');
    fs.writeFileSync(catalogMarkdownPath, renderCatalogMarkdown(catalog));
    return catalog;
}

if (require.main === module) {
    const catalog = buildCatalog();
    if (catalog) {
        console.log(`Generated catalog for ${catalog.total} skills.`);
    }
}

module.exports = { buildCatalog };
