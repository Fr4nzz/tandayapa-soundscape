import { useRef } from 'react'
import type { Detection } from '../types'
import { confColor } from '../lib/util'
import { DetectionCard } from './DetectionCard'

const CAP = 40
const groupIcon: Record<string, string> = { bird: '🐦', frog: '🐸', insect: '🦗' }

export interface SpeciesGroup {
  species: string
  common: string
  group: string
  items: Detection[] // sorted by confidence desc
}

export function SpeciesRow({ sp }: { sp: SpeciesGroup }) {
  const track = useRef<HTMLDivElement>(null)
  const scroll = (dir: number) =>
    track.current?.scrollBy({ left: dir * track.current.clientWidth * 0.85, behavior: 'smooth' })
  const top = sp.items[0]
  const c = confColor(top.conf)

  return (
    <section className="rise rounded-2xl border border-line bg-panel/50 p-3">
      <header className="mb-2.5 flex items-center gap-3 px-1">
        <div className="min-w-0">
          <h3 className="truncate font-display text-[21px] font-semibold leading-tight text-ink">
            <span className="mr-1.5 opacity-80">{groupIcon[sp.group] ?? '•'}</span>{sp.common}
          </h3>
          <p className="truncate font-mono text-[11px] italic text-muted">{sp.species}</p>
        </div>
        <span className="ml-auto rounded-full px-2 py-0.5 font-mono text-[12px] font-bold text-base"
          style={{ background: c, boxShadow: `0 0 12px ${c}55` }}>{top.conf.toFixed(2)}</span>
        <span className="whitespace-nowrap font-mono text-[11px] text-faint">
          {sp.items.length} clip{sp.items.length > 1 ? 's' : ''}
        </span>
        {sp.items.length > 1 && (
          <div className="flex gap-1">
            <ArrowBtn onClick={() => scroll(-1)}>‹</ArrowBtn>
            <ArrowBtn onClick={() => scroll(1)}>›</ArrowBtn>
          </div>
        )}
      </header>

      <div ref={track} className="flex snap-x gap-3 overflow-x-auto pb-2">
        {sp.items.slice(0, CAP).map((d, i) => (
          <div key={d.id} className="w-[330px] shrink-0 snap-start">
            <DetectionCard det={d} idx={i} />
          </div>
        ))}
        {sp.items.length > CAP && (
          <div className="grid w-[180px] shrink-0 place-items-center rounded-xl border border-dashed border-line p-4 text-center font-mono text-[11px] text-faint">
            +{sp.items.length - CAP} more<br />raise min-confidence to narrow
          </div>
        )}
      </div>
    </section>
  )
}

function ArrowBtn({ children, onClick }: { children: React.ReactNode; onClick: () => void }) {
  return (
    <button onClick={onClick}
      className="grid h-7 w-7 place-items-center rounded-md border border-line-2 font-mono text-muted transition hover:bg-panel-2 hover:text-ink">
      {children}
    </button>
  )
}
