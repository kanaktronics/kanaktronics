// Pulls the latest posts from the Avenoric blog's RSS feed into README.md,
// between the WRITING:START and WRITING:END markers. No dependencies.
import { readFile, writeFile } from 'node:fs/promises'

const FEED = 'https://avenoric.tech/feed.xml'
const COUNT = 4
const START = '<!-- WRITING:START -->'
const END = '<!-- WRITING:END -->'

const decode = (s) =>
  s.replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, '$1')
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'").replace(/&amp;/g, '&')
    .trim()

const pick = (xml, tag) => {
  const m = xml.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`))
  return m ? decode(m[1]) : ''
}

const res = await fetch(FEED, { headers: { 'user-agent': 'profile-readme-updater' } })
if (!res.ok) throw new Error(`Feed returned ${res.status}`)
const xml = await res.text()

const items = [...xml.matchAll(/<item>([\s\S]*?)<\/item>/g)]
  .map(([, block]) => ({
    title: pick(block, 'title'),
    link: pick(block, 'link'),
    date: new Date(pick(block, 'pubDate')),
    category: pick(block, 'category'),
  }))
  .filter((p) => p.title && /^https:\/\/avenoric\.tech\//.test(p.link))
  .sort((a, b) => b.date - a.date)
  .slice(0, COUNT)

if (items.length === 0) throw new Error('No posts found in feed')

const month = (d) => d.toLocaleString('en-US', { month: 'short', year: 'numeric', timeZone: 'UTC' })
const esc = (s) => s.replace(/([\[\]])/g, '\\$1')
const lines = items.map((p) =>
  `- **[${esc(p.title)}](${p.link})**<br><sub>${[p.category, month(p.date)].filter(Boolean).join(' · ')}</sub>`)

const readme = await readFile('README.md', 'utf8')
const a = readme.indexOf(START)
const b = readme.indexOf(END)
if (a === -1 || b === -1 || b < a) throw new Error('Writing markers missing from README.md')

const next = readme.slice(0, a + START.length) + '\n' + lines.join('\n') + '\n' + readme.slice(b)
if (next !== readme) {
  await writeFile('README.md', next)
  console.log(`Updated with ${items.length} posts`)
} else {
  console.log('No change')
}
