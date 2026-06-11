import { useState } from 'react'
import type { Recording, Detection } from '../types'
import { fmtDate, fmtClock } from '../lib/util'
import { Player } from './Player'

export function RecordingCard({ rec, idx }: { rec: Recording; idx: number }) {
  const [open, setOpen] = useState(false)
  // Player reads only audio/start/end; start === end => full-clip mode (no detection region)
  const clip = { audio: rec.url, start: 0, end: 0 } as Detection

  return (
    <article
      className="rise overflow-hidden rounded-xl border border-line bg-panel/80 backdrop-blur-sm transition hover:border-line-2"
      style={{ animationDelay: `${Math.min(idx, 16) * 28}ms` }}
    >
      <div className="flex flex-wrap items-center gap-x-2 gap-y-1.5 p-3.5">
        <span className={`font-display text-[17px] font-semibold ${rec.habitat === 'forest' ? 'text-forest' : 'text-pasture'}`}>
          {rec.habitat === 'forest' ? '🌳' : '🌾'} {rec.recorder}
        </span>
        <span className="font-mono text-[12px] text-muted">{fmtDate(rec.datetime)} · {fmtClock(rec.datetime)}</span>
        <div className="ml-auto flex flex-wrap gap-1.5 font-mono text-[11px]">
          <Tag>{rec.spacing} m</Tag>
          <Tag className="text-faint">{rec.daynight}</Tag>
          <Tag className="text-faint">{rec.moth}</Tag>
        </div>
      </div>

      {open ? (
        <Player det={clip} />
      ) : (
        <button
          onClick={() => setOpen(true)}
          className="w-full border-t border-line bg-panel-2/60 py-2.5 text-[13px] font-semibold text-moss transition hover:bg-panel-2"
        >▶ Load spectrogram &amp; audio</button>
      )}
    </article>
  )
}

function Tag({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <span className={`rounded-md border border-line bg-base/50 px-2 py-0.5 text-muted ${className}`}>{children}</span>
  )
}
