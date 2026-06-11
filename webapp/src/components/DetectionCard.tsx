import { useState } from 'react'
import type { Detection, ReferenceCall } from '../types'
import { confColor, fmtClock, fmtDate } from '../lib/util'
import { Player } from './Player'
import { ReferenceCalls } from './ReferenceCalls'

const groupIcon: Record<string, string> = { bird: '🐦', frog: '🐸', insect: '🦗' }

export function DetectionCard({ det, idx, refs }: { det: Detection; idx: number; refs?: ReferenceCall[] }) {
  const [open, setOpen] = useState(false)
  const [refOpen, setRefOpen] = useState(false)
  const c = confColor(det.conf)

  return (
    <article
      className="rise overflow-hidden rounded-xl border border-line bg-panel/80 backdrop-blur-sm transition hover:border-line-2"
      style={{ animationDelay: `${Math.min(idx, 16) * 28}ms` }}
    >
      <div className="flex items-start gap-3 p-3.5">
        <div className="min-w-0 flex-1">
          <h3 className="truncate font-display text-[19px] font-semibold leading-tight text-ink">
            <span className="mr-1.5 opacity-80">{groupIcon[det.group] ?? '•'}</span>
            {det.common}
          </h3>
          <p className="truncate font-mono text-[12px] italic text-muted">{det.species}</p>
        </div>
        <div className="flex flex-col items-end">
          <span
            className="rounded-full px-2.5 py-1 font-mono text-[13px] font-bold text-base"
            style={{ background: c, boxShadow: `0 0 14px ${c}55` }}
          >{det.conf.toFixed(2)}</span>
        </div>
      </div>

      <div className="flex flex-wrap gap-1.5 px-3.5 pb-3 font-mono text-[11px]">
        <Tag className={det.habitat === 'forest' ? 'text-forest' : 'text-pasture'}>
          {det.habitat} · {det.recorder}
        </Tag>
        <Tag>{det.day} · {det.spacing} m</Tag>
        <Tag>{fmtDate(det.time)} {fmtClock(det.time)}</Tag>
        <Tag>{det.daynight}</Tag>
        <Tag className="text-faint">{det.start.toFixed(1)}–{det.end.toFixed(1)}s</Tag>
      </div>

      {open ? (
        <Player det={det} />
      ) : (
        <button
          onClick={() => setOpen(true)}
          className="w-full border-t border-line bg-panel-2/60 py-2.5 text-[13px] font-semibold text-moss transition hover:bg-panel-2"
        >▶ Load spectrogram &amp; audio</button>
      )}

      {refOpen ? (
        <ReferenceCalls species={det.species} group={det.group} refs={refs} />
      ) : (
        <button
          onClick={() => setRefOpen(true)}
          className="w-full border-t border-line bg-base/30 py-2 text-[12px] font-medium text-muted transition hover:bg-panel-2 hover:text-moss"
        >🔊 Reference calls (compare ID)</button>
      )}
    </article>
  )
}

function Tag({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <span className={`rounded-md border border-line bg-base/50 px-2 py-0.5 text-muted ${className}`}>
      {children}
    </span>
  )
}
