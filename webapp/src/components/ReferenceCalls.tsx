import type { ReferenceCall } from '../types'

// strip the "~ " genus marker and "(katydid)" suffix for the search link
const cleanName = (s: string) => s.replace(/^~\s*/, '').replace(/\s*\(.*\)$/, '').trim()
const inatSearch = (s: string) =>
  `https://www.inaturalist.org/observations?taxon_name=${encodeURIComponent(cleanName(s))}&sounds=true`
const xcSearch = (s: string) =>
  `https://xeno-canto.org/explore?query=${encodeURIComponent(cleanName(s))}`

export function ReferenceCalls({ species, group, refs }: {
  species: string; group: string; refs: ReferenceCall[] | undefined
}) {
  if (group === 'insect' || !refs || refs.length === 0) {
    const note = group === 'insect'
      ? 'Reference audio is scarce for neotropical insects.'
      : 'No reference recording found for this taxon.'
    return (
      <div className="border-t border-line bg-base/30 px-3 py-2 font-mono text-[11px] text-faint">
        {note}{' '}
        <a className="text-moss underline hover:text-moss-bright" target="_blank" rel="noreferrer" href={inatSearch(species)}>iNaturalist ↗</a>
        {' · '}
        <a className="text-moss underline hover:text-moss-bright" target="_blank" rel="noreferrer" href={xcSearch(species)}>xeno-canto ↗</a>
      </div>
    )
  }
  return (
    <div className="border-t border-line bg-base/30 px-3 py-2.5">
      <p className="mb-1.5 font-mono text-[10px] uppercase tracking-widest text-faint">
        Reference calls — compare with the detection above
      </p>
      <div className="flex flex-col gap-2.5">
        {refs.map((r, i) => (
          <div key={i} className="flex flex-col gap-1">
            <audio controls preload="none" src={r.url} className="h-8 w-full" />
            <span className="font-mono text-[10px] text-faint">
              <span className="text-moss">{r.source}</span> · {r.place || 'unknown locality'} · {r.by}
              {r.license ? ` · ${r.license.toUpperCase()}` : ''} ·{' '}
              <a className="underline hover:text-moss" target="_blank" rel="noreferrer" href={r.obs_url}>source ↗</a>
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
